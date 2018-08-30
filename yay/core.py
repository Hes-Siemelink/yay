#
# Core tasks
#

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
        if action in handlers:
            result = invoke_handler(handlers[action], task[action], variables)
        else:
            print("Unknown action: {}".format(action))
    return result


def invoke_handler(handler, dataList, variables):
    if not is_list(dataList):
        dataList = [dataList]
    for rawData in dataList:
        result = invoke_single_handler(handler, rawData, variables)
    return result

def invoke_single_handler(handler, rawData, variables):
    data = vars.resolve_variables(rawData, variables)
    result = handler(data, variables)
    if not result == None:
        variables[RESULT_VARIABLE] = result
    return result

def foreach(data, variables):
    for item in data['in']:
        variable = data['var']

        stash = None
        if variable in variables:
            stash = variables[variable]
        variables[variable] = item

        process_task(data, variables)

        if (stash):
            variables[variable] = stash
        else:
            del variables[variable]

def store_result(data, variables):

    # set: varname
    # => will set the result into 'varname'
    if is_scalar(data):
        variables[data] = variables[RESULT_VARIABLE]
        return

    # set:
    #   varname: ${result.}
    # => will set the result into 'varname'. You can also use literal values or variables with paths.
    for var in data:
        variables[var] = data[var]

def noop(data, variables):
    yield

def assert_handler(data, variables):
    if 'equals' in data:
        assert_equals(data['equals'], variables)

def assert_equals(terms, variables):
    if len(terms) < 2:
        return
    if len(terms) > 2:
        raise Exception("Assert equals only takes 2 arguments.")

    assert terms[0] == terms[1], "\nExpected: {}\nActual:   {}".format(terms[0], terms[1])

#
# Variables
#

def process_variables(variableAssignment, variables):
    var = variableAssignment['var']

    content = None
    if 'value' in variableAssignment:
        content = variableAssignment['value']
    if 'path' in variableAssignment:
        content = get_json_path(content, variableAssignment['path'])
    if 'merge' in variableAssignment:
        content = merge_content(variableAssignment['merge'], variables)

    variables[var] = content

def merge_content(mergeList, variables):
    content = None
    for mergeItem in mergeList:
        if content and is_dict(content):
            content.update(mergeItem)
        if content and is_list(content):
            content.append(mergeItem)
        else:
            content = mergeItem

    return content


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

register('do', process_task)
register('foreach', foreach)
register('variables', process_variables)
register('print_json', print_json)
register('print_yaml', print_yaml)
register('name',  print_text)
register('print',  print_text)
register('var',  noop)
register('in',  noop)
register('set',  store_result)
register('assert',  assert_handler)
