import copy
import re
import time

from yay import conditions
from yay import vars

from yay.runtime import command_handler
from yay.execution import FlowBreak
from yay.util import *


#
# Control flow
#

# Do

@command_handler('Do', delayed_variable_resolver=True)
def do(data, context):
    return context.run_task(data)


@command_handler('Do in parallel', delayed_variable_resolver=True, list_processor=True)
def do_in_parallel(data, context):
    original_output = context.output()
    results = []

    for command in commands_as_list(data):
        context.output(original_output)
        result = context.run_task(command)
        results.append(result)

    return results


def commands_as_list(data):
    if is_list(data):
        return data
    elif is_dict(data):
        return [{key: data[key]} for key in data]
    else:
        raise YayException(f"data is not a command.")


# For each

@command_handler('For each', delayed_variable_resolver=True)
def for_each(data, context):
    variable_assignment = get_first_variable_assignment(data)

    output = []
    items = data[variable_assignment]
    items = vars.resolve_variables(items, context.variables)
    for value in as_list(items):
        data[variable_assignment] = value
        result = context.run_task({'Do': copy.deepcopy(data)})
        output.append(result)

    return output


def get_first_variable_assignment(data):
    for command in data:
        match = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, command)
        if match:
            return command
    return None


# Repeat

@command_handler('Repeat', delayed_variable_resolver=True)
def repeat(data, context):
    actions = get_parameter(data, 'Do')
    until = get_parameter(data, 'Until')

    finished = False
    while not finished:
        result = context.run_task({'Do': actions})

        if is_dict(until):
            until_copy = copy.deepcopy(until)
            until_copy = vars.resolve_variables(until_copy, context.variables)

            condition = conditions.parse_condition(until_copy)
            finished = condition.is_true()
        else:
            finished = (result == until)


# If and if any

@command_handler('If any', delayed_variable_resolver=True)
def if_any_statement(data, context):
    if_statement(data, context, True)


@command_handler('If', delayed_variable_resolver=True)
def if_statement(data, context, break_on_success=False):

    cons = conditions.pop_conditions(data)
    cons = vars.resolve_variables(cons, context.variables)
    condition = conditions.parse_condition(cons)

    if condition.is_true():
        context.run_task({'Do': data})

        # context.run_task({'Do': actions})

        if break_on_success:
            raise FlowBreak()


#
# Assert
#

@command_handler('Assert equals')
def assert_equals(data, context):
    actual = get_parameter(data, 'actual')
    expected = get_parameter(data, 'expected')

    assert expected == actual, "\nExpected: {}\nActual:   {}".format(expected, actual)


@command_handler('Assert that')
def assert_that(data, context):
    condition = conditions.parse_condition(data)

    if condition.is_true():
        return

    message = "\n{}".format(format_yaml(condition.as_dict()))
    if type(condition) is conditions.Equals:
        message = f"\nExpected: {condition.equals}\nActual:   {condition.object}"
    assert False, message


@command_handler('Expected output', list_processor=True)
def expect_output(data, context):
    assert data == context.output(), "\nExpected: {}\nActual:   {}".format(data, context.output())


#
# Variables
#

@command_handler('Set')
@command_handler('Set variable')
@command_handler('As')
def set_variable(data, context):
    # set: varname
    # => will set the output into 'varname'
    if is_scalar(data):
        context.variables[data] = context.output()
        return

    # set:
    #   var1: ${output}
    #   var2: Something else
    # => will set the output into 'varname'. You can also use literal values or variables with paths.
    for var in data:
        context.variables[var] = data[var]


@command_handler('Input')
def check_input(data, context):
    for input_parameter in data:
        if not input_parameter in context.variables:
            input_description = data[input_parameter]
            if 'default' in input_description:
                context.variables[input_parameter] = input_description['default']
            else:
                raise YayException("Variable not provided: " + input_parameter)


@command_handler('Output')
def return_input(data, context):
    return data


@command_handler('Raw data', delayed_variable_resolver=True)
def to_raw(data, context):
    if is_raw(data):
        return data

    return raw(data)


@command_handler('Live data')
def to_live(data, context):
    if not is_raw(data):
        return data

    return vars.resolve_variables(live(data), context.variables)


@command_handler('Apply variables')
def apply_variables(data, context):
    return raw(vars.resolve_variables(live(data), context.variables))

#
# Meta info
#

@command_handler('Task')
@command_handler('Test case')
def noop(data, context):
    pass


#
# Join and merge
#

@command_handler('Update')
@command_handler('Join')
def join(data, context):
    for var in data:
        join_single_variable(var, data[var], context.variables)


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
def merge(data, context):
    if is_dict(data):
        merge([context.output(), data], context.variables)
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


#
# Replace
#

@command_handler('Replace')
def replace_text(data, context):
    return replace(get_parameter(data, 'in'), get_parameter(data, 'part'), get_parameter(data, 'with'))


def replace(source, part, replacement):
    if is_scalar(source):
        return source.replace(part, replacement)

    if is_list(source):
        result = [replace(item, part, replacement) for item in source]
        return raw(result) if is_raw(source) else result

    if is_dict(source):
        result = {key: replace(value, part, replacement) for (key, value) in source.items()}
        return raw(result) if is_raw(source) else result

    return source


#
# Wait
#

@command_handler('Wait')
def wait(data, context):
    time.sleep(data)


#
# Printing
#

@command_handler('Print')
def print_text(data, context):
    print(data)


@command_handler('Print JSON')
@command_handler('Print as JSON')
def print_json(data, context):
    print_as_json(live_all(data))


@command_handler('Print YAML')
@command_handler('Print as YAML')
def print_yaml(data, context):
    print_as_yaml(live_all(data))
