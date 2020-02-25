import re

from yay import vars
from yay.util import *

#
# Execution logic
#

class CommandHandler():
    def __init__(self, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.handler_method = handler_method
        self.delayed_variable_resolver = delayed_variable_resolver
        self.list_processor = list_processor

class Runtime():

    def __init__(self, command_handlers = None):
        self.command_handlers = command_handlers if command_handlers else {}

    def add_command_handler(self, command, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.command_handlers[command] = CommandHandler(handler_method, delayed_variable_resolver, list_processor)

    def run_script(self, script, variables = {}):
        output = None
        for task_block in script:
            output = self.run_task(task_block, variables)
        return output

    def run_task(self, task_block, variables = {}):

        # Execute all commands in a task
        output = None
        for command in task_block:

            rawData = task_block[command]

            # Variable assignment
            variableMatch = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, command)
            if variableMatch:
                data = vars.resolve_variables(rawData, variables)
                variables[variableMatch.group(1)] = data

            # Execute handler
            elif command in self.command_handlers:
                output = self.run_command(self.command_handlers[command], rawData, variables)

            # Unknown action
            else:
                raise YayException("Unknown action: {}".format(command))

        return output


    def run_command(self, handler, data, variables):

        output_list = []

        if handler.list_processor:
            data = [data]

        # Process list as a sequence of actions
        for commandData in as_list(data):

            # Execute the handler
            try:
                output = self.run_single_command(handler, commandData, variables)
                output_list.append(output)

            # Stop processing on a break statement
            except FlowBreak as f:
                output_list.append(f.output)
                break

        # Store result
        output = output_list
        if not is_list(data) or handler.list_processor:
            output = output_list[0]

        if not output_list == [None]:
            variables[vars.OUTPUT_VARIABLE] = output
            variables[vars.DEPRECATED_RESULT_VARIABLE] = output

        return output

    def run_single_command(self, handler, rawData, variables):

        # Resolve variables
        # Don't resolve variables yet for Do or For each, etc. -- they will be resolved just in time
        if handler.delayed_variable_resolver:
            data = rawData
        else:
            data = vars.resolve_variables(rawData, variables)

        # Execute action
        return handler.handler_method(data, variables)


class FlowBreak(Exception):
    def __init__(self, output = None):
        self.output = output

