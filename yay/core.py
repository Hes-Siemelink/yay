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

        # Variable assignement
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

    first = True
    output_list = []

    if handler in list_processors:
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
    if not is_list(data) or handler in list_processors:
        output = output_list[0]

    if not output_list == [None]:
        variables[OUTPUT_VARIABLE] = output
        variables[DEPRECATED_RESULT_VARIABLE] = output

    return output

def execute_single_command(handler, rawData, variables):

    # Resolve variables
    # Don't resolve variables yet for Do or For each, etc. -- they will be resolved just in time
    if handler in delayed_variable_resolvers:
        data = rawData
    else:
        data = vars.resolve_variables(rawData, variables)

    # Execute action
    return handler(data, variables)


class FlowBreak(Exception):
    def __init__(self, output = None):
        self.output = output


#
# Control flow
#

def noop(data, variables):
    pass

# Do
def do(data, variables):
    return process_task(data, variables)

# For each
def foreach(data, variables):
    actions = get_parameter(data, 'Do')
    if len(data) != 2:
        raise YayException("'For each' needs exactly two parameters: 'Do' and the name of the variable.")

    loop_variable = get_foreach_variable(data)

    items = data[loop_variable]
    items = vars.resolve_variables(items, variables)

    for item in items:
        stash = None
        if loop_variable in variables:
            stash = variables[loop_variable]
        variables[loop_variable] = item

        execute_command(do, actions, variables)

        if (stash):
            variables[loop_variable] = stash
        else:
            del variables[loop_variable]

def get_foreach_variable(data):
    for variable in data:
        if variable == 'Do':
            continue
        return variable

# Repeat
def repeat(data, variables):
    actions = get_parameter(data, 'Do')
    until = get_parameter(data, 'Until')

    finished = False
    while not finished:
        result = execute_command(do, actions, variables)

        if is_dict(until):
            until_copy = copy.deepcopy(until)
            until_copy = vars.resolve_variables(until_copy, variables)

            condition = parse_condition(until_copy)
            finished = condition.is_true()
        else:
            finished = (result == until)

# Execute yay file

def execute_yay_file(data, variables, file = None):
    if file == None:
        file = get_parameter(data, 'file')

    # Read YAML script
    script = read_yaml_file(file)

    # Process all
    vars = copy.deepcopy(variables)
    if file in data:
        del data['file']
    vars.update(data)

    process_script(script, vars)

    return vars[OUTPUT_VARIABLE]

# If and if any

def if_any_statement(data, variables):
    if_statement(data, variables, True)

def if_statement(data, variables, break_on_success = False):
    actions = get_parameter(data, 'Do')

    del data['Do']
    data = vars.resolve_variables(data, variables)

    condition = parse_condition(data)

    if condition.is_true():
        execute_command(process_task, actions, variables)

        if break_on_success:
            raise FlowBreak()


#
# Assert
#

def assert_equals(data, variables):
    actual = get_parameter(data, 'actual')
    expected = get_parameter(data, 'expected')

    assert expected == actual, "\nExpected: {}\nActual:   {}".format(expected, actual)

def assert_that(data, variables):

    condition = parse_condition(data)

    if condition.is_true():
        return

    message = "\n{}".format(format_yaml(condition.as_dict()))
    if type(condition) is Equals:
        message = f"\nExpected: {condition.equals}\nActual:   {condition.object}"
    assert False, message

def expect_output(data, variables):
    actual = variables.get(OUTPUT_VARIABLE)
    expected = data

    assert expected == actual, "\nExpected: {}\nActual:   {}".format(expected, actual)

#
# Variables
#

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

def check_input(data, variables):
    for input_parameter in data:
        if not input_parameter in variables:
            input_description = data[input_parameter]
            if 'default' in input_description:
                variables[input_parameter] = input_description['default']
            else:
                raise YayException("Variable not provided: " + input_parameter)

def return_input(data, variables):
    return data

#
# Yay-context.yaml
#

def get_context(script_dir, selected_context):
    context_file = os.path.join(script_dir, 'yay-context.yaml')
    if os.path.isfile(context_file):
        all_contexts = read_yaml_file(context_file)[0]
        if selected_context in all_contexts:
            return all_contexts[selected_context]
        else:
            raise YayException(f"Context '{selected_context}' not found in yay-context.yaml")

    return {}


#
# Handlers
#

handlers = {}
delayed_variable_resolvers = []
list_processors = []

def register(type, handler, delayed_variable_resolver=False, list_processor=False):
    handlers[type] = handler

    if delayed_variable_resolver:
        delayed_variable_resolvers.append(handler)

    if list_processor:
        list_processors.append(handler)

def register_scripts(path):
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


register('Do', do, delayed_variable_resolver=True)
register('For each', foreach, delayed_variable_resolver=True)
register('Repeat', repeat, delayed_variable_resolver=True)

register('Execute yay file', execute_yay_file)

register('If', if_statement, delayed_variable_resolver=True)
register('If any', if_any_statement, delayed_variable_resolver=True)
register('Assert equals', assert_equals)
register('Assert that', assert_that)
register('Expected output', expect_output, list_processor=True)

register('Set', set_variable)
register('Set variable', set_variable)
register('As', set_variable)
register('Input', check_input)
register('Output', return_input)
