import re

from yay import vars
from yay.context import handlers
from yay.util import *
from yay.vars import OUTPUT_VARIABLE, DEPRECATED_RESULT_VARIABLE

#
# Execution logic
#

def process_script(script, variables = {}):
    output = None
    for task_block in script:
        output = process_task(task_block, variables)
    return output

def process_task(task_block, variables = {}):

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
        elif command in handlers:
            output = execute_command(handlers[command], rawData, variables)

        # Unknown action
        else:
            raise YayException("Unknown action: {}".format(command))

    return output


def execute_command(handler, data, variables):

    output_list = []

    if handler.list_processor:
        data = [data]

    # Process list as a sequence of actions
    for commandData in as_list(data):

        # Execute the handler
        try:
            output = execute_single_command(handler, commandData, variables)
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
        variables[OUTPUT_VARIABLE] = output
        variables[DEPRECATED_RESULT_VARIABLE] = output

    return output

def execute_single_command(handler, rawData, variables):

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



