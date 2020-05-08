import copy
import re

from yay import vars, conditions
from yay.util import *


def find_next_planned_step(step_group):
    for step in step_group['steps']:
        if step['status'] == 'Planned':
            return step
        if step['status'] == 'In progress':
            # TODO recursively find Planned steps
            return None
    return None


def collect_outputs(step_group):
    outputs = []
    for step in step_group['steps']:
        output = step.get('output')
        if output:
            outputs.append(output)

    if len(outputs) == 1:
        return outputs[0]

    return outputs


class StacklessExecutionContext():

    def __init__(self, variables = None, command_handlers = None):
        self.variables = variables if variables else {}
        self.command_handlers = command_handlers if command_handlers else {}


    def add_command_handler(self, command, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.command_handlers[command] = CommandHandler(command, handler_method, delayed_variable_resolver, list_processor)

    #
    # Execution
    #

    def run_script(self, script):

        persistent_run = self.create_persistent_script_run(script)

        print_as_yaml(script)
        print_as_yaml(persistent_run)

        self.run_next_step(persistent_run)

    def create_persistent_script_run(self, script):
        # run = {'variables': self.variables, 'command': 'Do', 'steps':[], 'status': 'Planned'}
        run = {'variables': {}, 'command': 'Do', 'steps':[], 'status': 'Planned'}
        for task_block in script:
            block = {'command': 'Do', 'status': 'Planned'}
            block['steps'] = self.create_persistent_command_step(task_block)
            run['steps'].append(block)
        return run

    def create_persistent_command_step(self, task_block):
        steps = []
        for command in task_block:
            data = {}
            if is_dict(task_block):
                data = task_block[command]
            elif is_list(task_block):
                command_key = list(command.keys())[0]
                data = command[command_key]
                command = command_key

            dict = {'command': command, 'data': data, 'status': 'Planned'}

            # Variable assignment
            variableMatch = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, command)
            if variableMatch:
                dict['command'] = 'Set variable'
                dict['data'] = {variableMatch.group(1): data}
                steps.append(dict)
                continue

            handler = self.command_handlers.get(command)

            if is_list(data) and not handler.list_processor and not command == 'Do':
                dict['join_output'] = True
                new_data = []
                for item in data:
                    new_data.append({command: item})
                command = 'Do'
                dict['command'] = 'Do'
                data = new_data

            if command == 'Do in parallel':
                dict['parallel'] = True
                command = 'Do'
                dict['command'] = 'Do'

            if command == 'Do':
                dict['steps'] = self.create_persistent_command_step(data)
                dict['join_output'] = is_list(data)
                del dict['data']
            elif command == 'For each':
                for_each_body = self.create_persistent_command_step(data)
                dict['data'] = for_each_body
                dict['join_output'] = True
            elif command in ['If', 'If any']:
                dict['steps'] = self.create_persistent_command_step(data['Do'])
                del data['Do']
            elif command == 'Repeat':
                dict['data'] = self.create_persistent_command_step(data['Do'])
                dict['until'] = data['Until']

            steps.append(dict)

        return steps

    def run_next_step(self, step_group):
        running = True

        while running:
            step = find_next_planned_step(step_group)
            if step:
                step['status'] = 'In progress'

                output = None
                try:
                    output = self.run_step(step)
                except FlowBreak as f:
                    running = False

                if not step_group.get('parallel'):
                    self.output(output)

                step['status'] = 'Done'

                # Handle 'Repeat until'
                if 'until' in step_group:
                    running = self.handle_until(step_group['until'], output)
                    if running:
                        step['status'] = 'In progress'
            else:
                running = False

        if step_group.get('join_output') == True:
            self.output(collect_outputs(step_group))
        step_group['status'] = 'Done'

    def handle_until(self, until, output):
        if is_dict(until):
            until_copy = copy.deepcopy(until)
            until_copy = vars.resolve_variables(until_copy, self.variables)

            condition = conditions.parse_condition(until_copy)
            running = not condition.is_true()
        else:
            running = (output != until)
        return running

    def run_step(self, step):

        command = step['command']

        # Handle flow control
        if 'Do' == command:
            self.run_next_step(step)
            return
        if 'For each' == command:
            self.expand_for_each(step)
            self.run_next_step(step)
            return
        if 'If' == command or 'If any' == command:
            data = vars.resolve_variables(step['data'], self.variables)
            condition = conditions.parse_condition(data)
            if condition.is_true():
                self.run_next_step(step)

                if 'If any' == command:
                    raise FlowBreak()
            return
        if 'Repeat' == command:
            step['steps'] = copy.deepcopy(step['data'])
            self.run_next_step(step)
            return

        # Unknown command
        if command not in self.command_handlers:
            raise YayException("Unknown action: {}".format(command))

        # Execute command
        output = self.run_single_command(self.command_handlers[command], step['data'])

        if output:
            step['output'] = output

        return output


    def run_single_command(self, handler, rawData):

        # Resolve variables
        # Don't resolve variables yet for Do or For each, etc. -- they will be resolved just in time
        if handler.delayed_variable_resolver:
            data = rawData
        else:
            data = vars.resolve_variables(rawData, self.variables)

        # Execute action
        return handler.handler_method(data, self)

    def output(self, value=None):
        if value:
            self.variables[vars.OUTPUT_VARIABLE] = value

        return self.variables.get(vars.OUTPUT_VARIABLE)

    def expand_for_each(self, for_each_command):
        for_each_command['steps'] = []
        set_variable_command = for_each_command['data'][0]['data']
        variable = list(set_variable_command.keys())[0]
        values = set_variable_command[variable]
        values = vars.resolve_variables(values, self.variables)
        for value in values:
            for_each_body = copy.deepcopy(for_each_command['data'])
            for_each_body[0]['data'][variable] = value
            for_each_command['steps'].extend(for_each_body)

class CommandHandler():
    def __init__(self, command, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.command = command
        self.handler_method = handler_method
        self.delayed_variable_resolver = delayed_variable_resolver
        self.list_processor = list_processor


class FlowBreak(Exception):
    def __init__(self, output=None):
        self.output = output
