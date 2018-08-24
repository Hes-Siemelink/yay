#
# Core tasks
#

from yay import vars

from yay.util import get_json_path
from yay.util import print_as_json
from yay.util import print_as_yaml

#
# Control flow
#

def process_tasks(tasks, variables = {}):
    for task in tasks:
        result = process_task(task, variables)
    return result

def process_task(task, variables = {}):
    result = None
    for action in task:
        if action in handlers:
            data = vars.resolve_variables(task[action], variables)
            result = handlers[action](data, variables)
            if not result == None:
                variables['result'] = result
        else:
            print("Unknown action: {}".format(action))
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
    if not 'result' in variables:
        return
    value = variables['result']

    if 'var' in data:
        var = data['var']
    else:
        var = 'result'


    if 'path' in data:
        value = get_json_path(value, data['path'])

    variables[var] = value

def noop(data, variables):
    yield


#
# Variables
#

def process_variables(variableTask, variables):
    if not variableTask: return

    for variableAssignment in variableTask:
        content = None
        if 'value' in variableAssignment:
            content = variableAssignment['value']
        if 'path' in variableAssignment:
            content = get_json_path(content, variableAssignment['path'])
        if 'merge' in variableAssignment:
            content = merge_content(variableAssignment['merge'], variables)

        var = variableAssignment['var']
        variables[var] = content

def merge_content(mergeList, variables):
    content = None
    for mergeItem in mergeList:
        if content and type(content) is dict:
            content.update(mergeItem)
        if content and isinstance(content, list):
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

register('do', process_tasks)
register('foreach', foreach)
register('variables', process_variables)
register('print_json', print_json)
register('print_yaml', print_yaml)
register('name',  print_text)
register('print',  print_text)
register('var',  noop)
register('in',  noop)
register('result',  store_result)