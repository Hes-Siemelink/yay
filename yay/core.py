#
# Core tasks
#

import copy
import re

from yay import vars
from yay.util import *

#
# Execution logic
#

RESULT_VARIABLE = 'result'

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
    results = []

    if handler in list_processors:
        data = [data]

    # Process list as a sequence of actions
    for taskData in as_list(data):

        # Execute the handler
        try:
            result = execute_single_task(handler, taskData, variables)
            results.append(result)

        # Stop processing on a break statement
        except FlowBreak as f:
            results.append(f.result)
            break

    # Store result
    result = results
    if not is_list(data) or handler in list_processors:
        result = results[0]

    if not results == [None]:
        variables[RESULT_VARIABLE] = result

    return result

def execute_single_task(handler, rawData, variables):

    # Resolve variables
    # Don't resolve variables yet for Do or For each, etc. -- they will be resolved just in time
    if handler in delayed_variable_resolvers:
        data = rawData
    else:
        data = vars.resolve_variables(rawData, variables)

    # Execute action
    result = handler(data, variables)

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
    return process_block(data, variables)

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

# Execute yay file

def execute_yay_file(data, variables, file = None):
    if file == None:
        file = get_parameter(data, 'file')

    # Read YAML script
    tasks = read_yaml_file(file)

    # Process all
    vars = copy.deepcopy(variables)
    if file in data:
        del data['file']
    vars.update(data)

    process_script(tasks, vars)

    return vars['result']

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

        if 'equals' in data:
            return Equals(object, data['equals'])

        if 'in' in data:
            return Contains(object, data['in'])

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

def return_result(data, variables):
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

def merge(data, variables):

    first = True
    result = None

    for item in data:

        if first:
            if is_dict(item):
                result = item
            else:
                result = as_list(item)
            first = False
            continue

        if is_dict(item):
            result.update(item)
        else:
            result.extend(as_list(item))

    return result

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

register('Execute yay file', execute_yay_file)

register('If', if_statement, delayed_variable_resolver=True)
register('If any', if_any_statement, delayed_variable_resolver=True)
register('Assert equals', assert_equals)
register('Assert that', assert_that)
register('Expected result', assert_result_equals, list_processor=True)

register('Set', set_variable)
register('Set variable', set_variable)
register('Result', set_variable)
register('As', set_variable)
register('Output', return_result)
register('Join', join)
register('Merge into variable', join)
register('Merge', merge, list_processor=True)

register('Print JSON', print_json)
register('Print as JSON', print_json)
register('Print YAML', print_yaml)
register('Print as YAML', print_yaml)
register('Name',  noop)
register('Task',  noop)
register('Test case',  noop)
register('Print',  print_text)
register('Replace',  replace_text)
