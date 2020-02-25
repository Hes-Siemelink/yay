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
command_handlers = {}

def add_command_handler(command, handler_method, delayed_variable_resolver=False, list_processor=False):
    command_handlers[command] = CommandHandler(handler_method, delayed_variable_resolver, list_processor)

def run_script(script, variables = {}):
    output = None
    for task_block in script:
        output = run_task(task_block, variables)
    return output

def run_task(task_block, variables = {}):

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
        elif command in command_handlers:
            output = run_command(command_handlers[command], rawData, variables)

        # Unknown action
        else:
            raise YayException("Unknown action: {}".format(command))

    return output


def run_command(handler, data, variables):

    output_list = []

    if handler.list_processor:
        data = [data]

    # Process list as a sequence of actions
    for commandData in as_list(data):

        # Execute the handler
        try:
            output = run_single_command(handler, commandData, variables)
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

def run_single_command(handler, rawData, variables):

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


