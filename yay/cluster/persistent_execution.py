import copy
import re

from yay import vars
from yay.util import *


def save(persistent_run):
    pass

def find_next_planned_step(step_group):
    for step in step_group['steps']:
        if step['status'] == 'Planned':
            return step
        if step['status'] == 'In progress':
            # TODO recursively find Planned steps
            return None
    return None



class PersistentExecutionContext():

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
        save(persistent_run)
        # print_as_json(persistent_run)

        self.run_next_step(persistent_run)

    def create_persistent_script_run(self, script):
        run = {'variables': self.variables, 'command': 'Do', 'steps':[], 'status': 'Planned'}
        for task_block in script:
            block = {'command': 'Do', 'status': 'Planned'}
            block['steps'] = self.create_persistent_command_step(task_block)
            run['steps'].append(block)
        return run

    def create_persistent_command_step(self, task_block):
        steps = []
        for command in task_block:
            data =  task_block[command]
            dict = {'command': command, 'data': data, 'status': 'Planned'}

            # Variable assignment
            variableMatch = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, command)
            if variableMatch:
                dict['command'] = 'Set variable'
                dict['data'] = {variableMatch.group(1): data}
                steps.append(dict)
                continue

            handler = self.command_handlers.get(command)

            if command == 'Do':
                dict['steps'] = self.create_persistent_command_step(data)
                del dict['data']
            elif command == 'For each':
                for_each_body = self.create_persistent_command_step(data)
                dict['data'] = for_each_body

            steps.append(dict)

        return steps

    def run_next_step(self, persistent_run):
        running = True

        while running:
            step = find_next_planned_step(persistent_run)
            if step:
                step['status'] = 'In progress'
                save(persistent_run)

                self.run_task(step)

                step['status'] = 'Done'
                save(persistent_run)
            else:
                persistent_run['status'] = 'Done'
                running = False

    def run_task(self, task_block):

        if task_block['command'] == 'Do':
            self.run_next_step(task_block)
            return

        if task_block['command'] == 'For each':
            expand_for_each(task_block)

            self.run_next_step(task_block)
            return

        command = task_block['command']

        if command not in self.command_handlers:
            raise YayException("Unknown action: {}".format(command))

        output = self.run_single_command(self.command_handlers[command], task_block['data'])

        self.output(output)


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
            self.variables[vars.DEPRECATED_RESULT_VARIABLE] = value

        return self.variables.get(vars.OUTPUT_VARIABLE)

def expand_for_each(for_each_command):
    for_each_command['steps'] = []
    set_variable_command = for_each_command['data'][0]['data']
    variable = list(set_variable_command.keys())[0]
    values = set_variable_command[variable]
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
