import copy
import re

import pymongo
from bson.objectid import ObjectId

from yay import vars, conditions
from yay.util import *

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
yay_db = mongo_client["yay-db"]

script_collection = yay_db["scripts"]


def find_next_planned_step(step_group):
    for step in step_group['steps']:
        if step['status'] == 'Planned':
            return (step, step_group)
        if step['status'] == 'In progress':
            if 'steps' in step:
                next_step = find_next_planned_step(step)
                return (step, next_step) if next_step else (step, step_group)
            else:
                return (None, None)
    return (None, None)


def collect_outputs(step_group):
    outputs = []
    for step in step_group['steps']:
        output = step.get('output')
        if output:
            outputs.append(output)

    if len(outputs) == 1:
        return outputs[0]

    return outputs


class PersistentExecutionContext():

    def __init__(self, variables=None, command_handlers=None):
        self.variables = variables if variables else {}
        self.command_handlers = command_handlers if command_handlers else {}
        self.script = None

    def add_command_handler(self, command, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.command_handlers[command] = CommandHandler(command, handler_method, delayed_variable_resolver, list_processor)

    #
    # Execution
    #

    def run_from_database(self, id):
        self.script = script_collection.find_one({"_id": ObjectId(id)})

        while self.script['status'] != 'Completed':
            self.run_next_step(self.script)

    def save(self, script):
        self.script = script_collection.insert_one(script)

        print(f"ID: {self.script.inserted_id}")

        return self.script

    def update(self):
        script_collection.update({'_id':self.script['_id']}, {"$set": self.script}, upsert=False)

    def run_script(self, script):
        persistent_script = self.to_persistent_script(script)

        # print_as_yaml(persistent_run)

        persistent_script = self.save(persistent_script)

        self.run_from_database(persistent_script.inserted_id)

    def to_persistent_script(self, script):
        # run = {'variables': self.variables, 'command': 'Do', 'steps':[], 'status': 'Planned'}
        run = {'variables': {}, 'command': 'Do', 'steps':[], 'status': 'Planned'}
        for task_block in script:
            block = {
                'command': 'Do',
                'status': 'Planned',
                'steps': self.to_persistent_steps(task_block)
            }
            run['steps'].append(block)
        return run

    def to_persistent_steps(self, task_block):
        return [self.to_persistent_step(command, task_block) for command in task_block]

    def to_persistent_step(self, command, task_block):
        command, data = self.unpack(command, task_block)

        step = {'status': 'Planned'}

        # Variable assignment
        variableMatch = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, command)
        if variableMatch:
            step['command'] = 'Set variable'
            step['data'] = {variableMatch.group(1): data}
            return step

        # Expand list of arguments to individual invocations
        handler = self.command_handlers.get(command)
        if is_list(data) and not handler.list_processor and not command == 'Do':
            step['join_output'] = True
            data = [{command: item} for item in data]
            command = 'Do'

        # Convert 'Do in parallel' to 'Do'
        if command == 'Do in parallel':
            step['parallel'] = True
            step['join_output'] = True
            command = 'Do'

        # Control structures
        if command == 'Do':
            step['steps'] = self.to_persistent_steps(data)
            step['join_output'] = is_list(data)
            data = {}
        elif command == 'For each':
            data = self.to_persistent_steps(data)
            step['join_output'] = True
        elif command in ['If', 'If any']:
            step['steps'] = self.to_persistent_steps(data['Do'])
            del data['Do']
        elif command == 'Repeat':
            step['until'] = data['Until']
            data = self.to_persistent_steps(data['Do'])

        step['command'] = command
        step['data'] = data

        return step

    def unpack(self, command, task_block):
        if is_dict(command):
            command_key = list(command.keys())[0]
            return command_key, command[command_key]
        else:
            return command, task_block[command]

    def run_next_step(self, step_group):
        step, parent = find_next_planned_step(step_group)

        if not step:
            self.complete_group(step_group)
            return

        if 'steps' in step and step['status'] == 'In progress':
            self.complete_group(step)
            return

        step['status'] = 'In progress'

        self.update()

        output = None
        try:
            output = self.run_step(step)
        except FlowBreak as f:
            self.complete_group(step_group)

        if 'steps' not in step:
            if not parent.get('parallel'):
                self.output(output)

            step['status'] = 'Completed'
            # Handle 'Repeat until'
            if 'until' in step_group:
                running = self.handle_until(step_group['until'], output)
                if running:
                    step['status'] = 'In progress'
        self.update()

    def complete_group(self, step_group):
        if step_group.get('join_output') == True:
            self.output(collect_outputs(step_group))
        step_group['status'] = 'Completed'
        self.update()

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
