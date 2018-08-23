#
# Core tasks
#

from yppy import vars

from yppy.util import get_json_path
from yppy.util import print_as_json
from yppy.util import print_as_yaml

#
# Control flow
#

def process_tasks(tasks, variables = {}):
    for task in tasks:
        last_result = process_task(task, variables)
    return last_result

def process_task(task, variables = {}):
    last_result = None
    for action in task:
        if action in handlers:
            data = vars.resolve_variables(task[action], variables)
            last_result = handlers[action](data, variables)
        else:
            print("Unknown action: {}".format(action))
    return last_result

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
