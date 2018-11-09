#
# Core tasks
#
import re

from yay import vars
from yay.util import *

#
# Control flow
#
RESULT_VARIABLE = 'result'

def process_tasks(tasks, variables = {}):
    for task in tasks:
        result = process_task(task, variables)
    return result

def process_task(task, variables = {}):
    result = None
    for action in task:
        variableMatch = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, action)
        if variableMatch:
            variables[variableMatch.group(1)] = task[action]
        elif action in handlers:
            result = invoke_handler(handlers[action], task[action], variables)
        else:
            raise YayException("Unknown action: {}".format(action))
    return result


def invoke_handler(handler, data, variables):
    for rawData in as_list(data):
        result = invoke_single_handler(handler, rawData, variables)
    return result

def invoke_single_handler(handler, rawData, variables):
    data = vars.resolve_variables(rawData, variables)
    result = handler(data, variables)
    if not result == None:
        variables[RESULT_VARIABLE] = result
    return result

def foreach(data, variables):
    actions = get_parameter(data, 'Do')
    if len(data) != 2:
        raise YayException("Foreach needs exactly two parameters: 'do' and the name of the variable.")

    variable = get_foreach_variable(data)

    for item in data[variable]:
        stash = None
        if variable in variables:
            stash = variables[variable]
        variables[variable] = item

        invoke_handler(process_task, actions, variables)

        if (stash):
            variables[variable] = stash
        else:
            del variables[variable]

def get_foreach_variable(data):
    for variable in data:
        if variable == 'Do':
            continue
        return variable

def noop(data, variables):
    pass

def assert_equals(data, variables):
    actual = get_parameter(data, 'actual')
    expected = get_parameter(data, 'expected')

    assert expected == actual, "\nExpected: {}\nActual:   {}".format(expected, actual)

#
# Variables
#

def set_variable(data, variables):

    # set: varname
    # => will set the result into 'varname'
    if is_scalar(data):
        variables[data] = variables[RESULT_VARIABLE]
        return

    # set:
    #   var1: ${result}
    #   var2: Something else
    # => will set the result into 'varname'. You can also use literal values or variables with paths.
    for var in data:
        variables[var] = data[var]

def result(data, variables):
    return data

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

#
#
#

def replace_text(data, variables):
    part = get_parameter(data, 'part')
    text = get_parameter(data, 'in')
    replacement = get_parameter(data, 'with')

    return text.replace(part, replacement)


#
# Printing
#

def print_text(data, variables):
    print(data)

def print_json(data, variables):
    print_as_json(data)

def print_yaml(data, variables):
    print_as_yaml(data)

#
# Handlers
#

handlers = {}
def register(type, handler):
    handlers[type] = handler

register('Do', process_task)
register('For each', foreach)
register('Assert equals', assert_equals)

register('Set', set_variable)
register('Set variable', set_variable)
register('Result', result)
register('Join', join)

register('Print JSON', print_json)
register('Print YAML', print_yaml)
register('Name',  noop)
register('Task',  noop)
register('Test case',  noop)
register('Print',  print_text)
register('Replace',  replace_text)
