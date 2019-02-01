#
# Core tasks
#
import re

from yay import vars
from yay.util import *

#
# Execution logic
#

RESULT_VARIABLE = 'result'
FIRST_EXECUTION_IN_LIST = '_first_execution_of_list'

def process_script(script, variables = {}):
    result = None
    for block in script:
        result = process_block(block, variables)
    return result

def process_block(block, variables = {}):

    # Execute all handlers in a task
    result = None
    for task in block:

        rawData = block[task]

        # Variable assignement
        variableMatch = re.search(vars.VariableMatcher.ONE_VARIABLE_ONLY_REGEX, task)
        if variableMatch:
            data = vars.resolve_variables(rawData, variables)
            variables[variableMatch.group(1)] = data

        # Execute handler
        elif task in handlers:
            result = execute_task(handlers[task], rawData, variables)

        # Unknown action
        else:
            raise YayException("Unknown action: {}".format(task))

    return result


def execute_task(handler, data, variables):

    first = True

    # Process list as a sequence of actions
    for taskData in as_list(data):

        # Indicates if this is the first execution of a list
        # Hack to get 'Merge' working
        if first and is_list(data):
            variables[FIRST_EXECUTION_IN_LIST] = True
            first = False

        # Execute the handler
        try:
            result = execute_single_task(handler, taskData, variables)

        # Stop processing on a break statement
        except FlowBreak as f:
            result = f.result
            break

        finally:
            if FIRST_EXECUTION_IN_LIST in variables:
                del variables[FIRST_EXECUTION_IN_LIST]

    return result

def execute_single_task(handler, rawData, variables):

    # Resolve variables
    # Don't resolve variables if handler is Do or For each -- they will be resolved just in time
    if handler in [do, foreach, if_statement, if_any_statement]:
        data = rawData
    else:
        data = vars.resolve_variables(rawData, variables)

    # Execute action
    result = handler(data, variables)

    # Store result
    if not result == None:
        variables[RESULT_VARIABLE] = result

    return result

class FlowBreak(Exception):
    def __init__(self, result = None):
        self.result = result


#
# Control flow
#

def noop(data, variables):
    pass

# Do
def do(data, variables):
    process_block(data, variables)

# For each
def foreach(data, variables):
    actions = get_parameter(data, 'Do')
    if len(data) != 2:
        raise YayException("'For each' needs exactly two parameters: 'do' and the name of the variable.")

    loop_variable = get_foreach_variable(data)

    items = data[loop_variable]
    items = vars.resolve_variables(items, variables)

    for item in items:
        stash = None
        if loop_variable in variables:
            stash = variables[loop_variable]
        variables[loop_variable] = item

        execute_task(do, actions, variables)

        if (stash):
            variables[loop_variable] = stash
        else:
            del variables[loop_variable]

def get_foreach_variable(data):
    for variable in data:
        if variable == 'Do':
            continue
        return variable

# If and if any

def if_any_statement(data, variables):
    if_statement(data, variables, True)

def if_statement(data, variables, break_on_success = False):
    actions = get_parameter(data, 'Do')

    del data['Do']
    data = vars.resolve_variables(data, variables)

    condition = parse_condition(data)

    if condition.is_true():
        execute_task(process_block, actions, variables)

        if break_on_success:
            raise FlowBreak()

def parse_condition(data):
    if 'object' in data:
        object = get_parameter(data, 'object')

        equals = data.get('equals')
        if (equals):
            return Equals(object, equals)

        list = data.get('in')
        if (list):
            return Contains(object, list)

        raise YayException("Condition with 'object' should have either 'equals' or 'in'.")

    elif 'all' in data:
        all = get_parameter(data, 'all')
        list = [parse_condition(condition) for condition in all]
        return All(list)

    elif 'any' in data:
        any = get_parameter(data, 'any')
        list = [parse_condition(condition) for condition in any]
        return Any(list)

    else:
        raise YayException("Condition needs 'object', 'all' or 'any'.")


class Equals():

    def __init__(self, object, equals):
        self.object = object
        self.equals = equals

    def is_true(self):
        return self.object == self.equals

    def __repr__(self):
        return f"{self.object} == {self.equals}"

    def as_dict(self):
        dict = {'object': as_dict(self.object), 'equals' : as_dict(self.equals)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict

class Contains():

    def __init__(self, object, list):
        self.object = object
        self.list = list

    def is_true(self):
        return self.object in self.list

    def __repr__(self):
        return f"{self.object} in {self.list}"

    def as_dict(self):
        dict = {'object': as_dict(self.object), 'in' : as_dict(self.list)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict

class All():

    def __init__(self, list):
        self.list = list

    def is_true(self):
        return all([object.is_true() for object in self.list])

    def __repr__(self):
        return f"ALL {self.list}"

    def as_dict(self):
        dict = {'all': as_dict(self.list)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict

class Any():

    def __init__(self, list):
        self.list = list

    def is_true(self):
        return any([object.is_true() for object in self.list])

    def __repr__(self):
        return f"ANY {self.list}"

    def as_dict(self):
        dict = {'any': as_dict(self.list)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict

def as_dict(object):
    if hasattr(object, 'as_dict'):
        return object.as_dict()

    if is_list(object):
        return [as_dict(item) for item in object]

    if is_dict(object):
        return { key: as_dict(value) for key, value in object.items() }

    return object

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

def assert_result_equals(data, variables):
    actual = variables.get(RESULT_VARIABLE)
    expected = data

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

def merge(data, variables):
    if variables.get(FIRST_EXECUTION_IN_LIST):
        variables[RESULT_VARIABLE] = data
        return

    value = variables[RESULT_VARIABLE]
    if is_dict(value):
        value.update(data)
    elif is_list(value):
        value.extend(as_list(data))

    return value

#
# Replace
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

register('Do', do)
register('For each', foreach)
register('If', if_statement)
register('If any', if_any_statement)
register('Assert equals', assert_equals)
register('Assert that', assert_that)
register('Expected result', assert_result_equals)

register('Set', set_variable)
register('Set variable', set_variable)
register('Result', set_variable)
register('Join', join)
register('Merge into variable', join)
register('Merge', merge)

register('Print JSON', print_json)
register('Print as JSON', print_json)
register('Print YAML', print_yaml)
register('Print as YAML', print_yaml)
register('Name',  noop)
register('Task',  noop)
register('Test case',  noop)
register('Print',  print_text)
register('Replace',  replace_text)
