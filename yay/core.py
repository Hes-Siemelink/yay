#
# Core execution logic and command handlers
#

import copy
import re

from yay import vars
from yay.util import *
from yay.conditions import parse_condition, Equals

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


#
# Control flow
#

def noop(data, variables):
    pass

# Do
@command_handler('Do', delayed_variable_resolver=True)
def do(data, variables):
    return process_task(data, variables)

# For each
@command_handler('For each', delayed_variable_resolver=True)
def foreach(data, variables):
    actions = get_parameter(data, 'Do')
    if len(data) != 2:
        raise YayException("'For each' needs exactly two parameters: 'Do' and the name of the variable.")

    loop_variable = get_foreach_variable(data)

    items = data[loop_variable]
    items = vars.resolve_variables(items, variables)

    output = []
    for item in items:
        stash = None
        if loop_variable in variables:
            stash = variables[loop_variable]
        variables[loop_variable] = item

        result = execute_command(handlers['Do'], actions, variables)
        output.append(result)

        if (stash):
            variables[loop_variable] = stash
        else:
            del variables[loop_variable]

    return output

def get_foreach_variable(data):
    for variable in data:
        if variable == 'Do':
            continue
        return variable

# Repeat

@command_handler('Repeat', delayed_variable_resolver=True)
def repeat(data, variables):
    actions = get_parameter(data, 'Do')
    until = get_parameter(data, 'Until')

    finished = False
    while not finished:
        result = execute_command(handlers['Do'], actions, variables)

        if is_dict(until):
            until_copy = copy.deepcopy(until)
            until_copy = vars.resolve_variables(until_copy, variables)

            condition = parse_condition(until_copy)
            finished = condition.is_true()
        else:
            finished = (result == until)

# Execute yay file

@command_handler('Execute yay file')
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

# If and if any

@command_handler('If any', delayed_variable_resolver=True)
def if_any_statement(data, variables):
    if_statement(data, variables, True)

@command_handler('If', delayed_variable_resolver=True)
def if_statement(data, variables, break_on_success = False):
    actions = get_parameter(data, 'Do')

    del data['Do']
    data = vars.resolve_variables(data, variables)

    condition = parse_condition(data)

    if condition.is_true():
        execute_command(Handler(process_task), actions, variables)

        if break_on_success:
            raise FlowBreak()


#
# Assert
#

@command_handler('Assert equals')
def assert_equals(data, variables):
    actual = get_parameter(data, 'actual')
    expected = get_parameter(data, 'expected')

    assert expected == actual, "\nExpected: {}\nActual:   {}".format(expected, actual)

@command_handler('Assert that')
def assert_that(data, variables):

    condition = parse_condition(data)

    if condition.is_true():
        return

    message = "\n{}".format(format_yaml(condition.as_dict()))
    if type(condition) is Equals:
        message = f"\nExpected: {condition.equals}\nActual:   {condition.object}"
    assert False, message

@command_handler('Expected output', list_processor=True)
def expect_output(data, variables):
    actual = variables.get(OUTPUT_VARIABLE)
    expected = data

    assert expected == actual, "\nExpected: {}\nActual:   {}".format(expected, actual)

#
# Variables
#

@command_handler('Set')
@command_handler('Set variable')
@command_handler('As')
def set_variable(data, variables):

    # set: varname
    # => will set the output into 'varname'
    if is_scalar(data):
        variables[data] = variables[OUTPUT_VARIABLE]
        return

    # set:
    #   var1: ${output}
    #   var2: Something else
    # => will set the output into 'varname'. You can also use literal values or variables with paths.
    for var in data:
        variables[var] = data[var]

@command_handler('Input')
def check_input(data, variables):
    for input_parameter in data:
        if not input_parameter in variables:
            input_description = data[input_parameter]
            if 'default' in input_description:
                variables[input_parameter] = input_description['default']
            else:
                raise YayException("Variable not provided: " + input_parameter)

@command_handler('Output')
def return_input(data, variables):
    return data

#
# Yay-context.yaml
#

def get_context(script_dir, profile_name):
    context_file = os.path.join(script_dir, 'yay-context.yaml')
    if not os.path.isfile(context_file):
        return {}

    context = read_yaml_file(context_file)[0]
    apply_profile(context, profile_name)

    return context


def apply_profile(context, profile_name):
    profiles = context.pop('profiles', None)
    if profile_name:
        if profiles and profile_name in profiles:
            dict_merge(context, profiles[profile_name])
        else:
            raise YayException(f"Profile '{profile_name}' not found in yay-context.yaml")


def dict_merge(context, profile):
    for key in profile:
        if key in context:
            context[key].update(profile[key])
        else:
            context[key] = profile[key]
