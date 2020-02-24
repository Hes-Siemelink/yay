#
# Core execution logic and command handlers
#

import copy
import re

from yay import vars
from yay.util import *

#
# Execution logic
#

OUTPUT_VARIABLE = 'output'
DEPRECATED_RESULT_VARIABLE = 'result'

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

#
# Command handlers
#

handlers = {}

class Handler():

    def __init__(self, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.handler_method = handler_method
        self.delayed_variable_resolver = delayed_variable_resolver
        self.list_processor = list_processor

def register(command, handler_method, delayed_variable_resolver=False, list_processor=False):
    handlers[command] = Handler(handler_method, delayed_variable_resolver, list_processor)

def command_handler(command, delayed_variable_resolver=False, list_processor=False):
    def inner_decorator(handler_function):
        register(command, handler_function, delayed_variable_resolver=delayed_variable_resolver, list_processor=list_processor)
        return handler_function
    return inner_decorator

def register_scripts(path):

    # Resolve ~ for home dir
    path = os.path.expanduser(path)

    # Create a custom handler for each script in the directory by
    # routing it to 'exectute_yay_file' using a lambda function.
    for filename in os.listdir(path):
        if filename.endswith('.yay'):
            handler_name = to_handler_name(filename)
            filename = os.path.join(path, filename)
            register(handler_name,
                     lambda data, variables, file = filename:
                     execute_yay_file(data, variables, file))

def to_handler_name(filename):
    filename = filename.replace('.yay', '')
    filename = filename.replace('-', ' ')
    return filename


def execute_yay_file(data, variables, file = None):
    if file == None:
        file = get_parameter(data, 'file')

    # Read YAML script
    script = read_yaml_file(file)

    # Process all
    vars = copy.deepcopy(variables)
    if file in data:
        del data['file']

    # FIXME handle case if data is str or list
    vars.update(data)

    process_script(script, vars)

    return vars.get(OUTPUT_VARIABLE)
