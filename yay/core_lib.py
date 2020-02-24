import copy
import time

import yay.context
import yay.vars
from yay import conditions
from yay import execution
from yay import vars
from yay.context import command_handler
from yay.util import *

#
# Control flow
#

# Do
@command_handler('Do', delayed_variable_resolver=True)
def do(data, variables):
    return execution.process_task(data, variables)

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

        result = execution.execute_command(yay.context.handlers['Do'], actions, variables)
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
        result = execution.execute_command(yay.context.handlers['Do'], actions, variables)

        if is_dict(until):
            until_copy = copy.deepcopy(until)
            until_copy = vars.resolve_variables(until_copy, variables)

            condition = conditions.parse_condition(until_copy)
            finished = condition.is_true()
        else:
            finished = (result == until)

# Execute yay file

@command_handler('Execute yay file')
def execute_yay_file(data, variables, file = None):
    return yay.context.execute_yay_file(data, variables, file)

# If and if any

@command_handler('If any', delayed_variable_resolver=True)
def if_any_statement(data, variables):
    if_statement(data, variables, True)

@command_handler('If', delayed_variable_resolver=True)
def if_statement(data, variables, break_on_success = False):
    actions = get_parameter(data, 'Do')

    del data['Do']
    data = vars.resolve_variables(data, variables)

    condition = conditions.parse_condition(data)

    if condition.is_true():
        execution.execute_command(yay.context.Handler(execution.process_task), actions, variables)

        if break_on_success:
            raise execution.FlowBreak()


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

    condition = conditions.parse_condition(data)

    if condition.is_true():
        return

    message = "\n{}".format(format_yaml(condition.as_dict()))
    if type(condition) is conditions.Equals:
        message = f"\nExpected: {condition.equals}\nActual:   {condition.object}"
    assert False, message

@command_handler('Expected output', list_processor=True)
def expect_output(data, variables):
    actual = variables.get(yay.vars.OUTPUT_VARIABLE)
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
        variables[data] = variables[yay.vars.OUTPUT_VARIABLE]
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
# Meta info
#

@command_handler('Task')
@command_handler('Test case')
def noop(data, variables):
    pass

#
# Join and merge
#

@command_handler('Join')
def join(data, variables):
    for var in data:
        join_single_variable(var, data[var], variables)

def join_single_variable(var, updates, variables):
    value = variables.get(var)
    for update in as_list(updates):
        if value is None:
            value = update
            continue

        if is_dict(value):
            value.update(update)
        elif is_list(value):
            value.extend(as_list(update))
    variables[var] = value

@command_handler('Merge', list_processor=True)
def merge(data, variables):

    if is_dict(data):
        merge([variables[yay.vars.OUTPUT_VARIABLE], data], variables)
        return

    first = True
    output = None

    for item in data:
        if first:
            if is_dict(item):
                output = item
            else:
                output = as_list(item)
            first = False
            continue

        if is_dict(item):
            output.update(item)
        else:
            output.extend(as_list(item))

    return output

@command_handler('Apply variables')
def apply_variables(data, variables):
    return raw(vars.resolve_variables(live(data), variables))

#
# Replace
#

@command_handler('Replace')
def replace_text(data, variables):
    part = get_parameter(data, 'part')
    text = get_parameter(data, 'in')
    replacement = get_parameter(data, 'with')

    return text.replace(part, replacement)

#
# Wait
#

@command_handler('Wait')
def wait(data, variables):
    time.sleep(data)

#
# Printing
#

@command_handler('Print')
def print_text(data, variables):
    print(data)

@command_handler('Print JSON')
@command_handler('Print as JSON')
def print_json(data, variables):
    print_as_json(data)

@command_handler('Print YAML')
@command_handler('Print as YAML')
def print_yaml(data, variables):
    print_as_yaml(data)
