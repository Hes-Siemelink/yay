import re

from yay import vars
from yay.util import *

#
# Execution logic
#

def run_script(script, context):
    output = None
    for task_block in script:
        output = run_task(task_block, context)
    return output

def run_task(task_block, context):

    # Execute all commands in a task
    output = None
    for command in task_block:

        rawData = task_block[command]

        # Variable assignment
        variableMatch = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, command)
        if variableMatch:
            data = vars.resolve_variables(rawData, context.variables)
            context.variables[variableMatch.group(1)] = data

        # Execute handler
        elif command in context.command_handlers:
            output = run_command(context.command_handlers[command], rawData, context)

        # Unknown action
        else:
            raise YayException("Unknown action: {}".format(command))

    return output


def run_command(handler, data, context):

    output_list = []

    if handler.list_processor:
        data = [data]

    # Process list as a sequence of actions
    for commandData in as_list(data):

        # Execute the handler
        try:
            output = run_single_command(handler, commandData, context)
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
        context.variables[vars.OUTPUT_VARIABLE] = output
        context.variables[vars.DEPRECATED_RESULT_VARIABLE] = output

    return output

def run_single_command(handler, rawData, context):

    # Resolve variables
    # Don't resolve variables yet for Do or For each, etc. -- they will be resolved just in time
    if handler.delayed_variable_resolver:
        data = rawData
    else:
        data = vars.resolve_variables(rawData, context.variables)

    # Execute action
    return handler.handler_method(data, context)


class FlowBreak(Exception):
    def __init__(self, output = None):
        self.output = output

