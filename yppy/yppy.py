#!/usr/bin/env python3
import sys
import os
import json
import yaml
import requests
from jsonpath_rw import jsonpath, parse
import re

global_context = {}
handlers = {}

def main():
    # Parse arguments
    endpoint = sys.argv[1]
    fileArgument = sys.argv[2]

    global_context['endpoint'] = endpoint

    # Set up handlers
    handlers['do'] = process_tasks
    handlers['variables'] = process_variables
    handlers['request'] = process_request
    handlers['print_json'] = print_json
    handlers['name'] = print_text
    handlers['print'] = print_text
    handlers['var'] = noop
    handlers['in'] = noop
    handlers['foreach'] = foreach

    # Read YAML files
    tasks = read_yaml_files(fileArgument)

    # Process all
    result = process_tasks(tasks)
    if result: print_as_json(result)

def process_tasks(tasks, variables = {}):
    for task in tasks:
        last_result = process_task(task, variables)
    return last_result

def process_task(task, variables = {}):
    for action in task:
        if action in handlers:
            data = resolve_variables(task[action], variables)
            last_result = handlers[action](data, variables)
        else:
            print("Unknown action: {}".format(action))
    return last_result

#
# HTTP Request task
#

def process_request(data, variables):
    result = send_request(data, variables)

    if (type(result) is dict):
        variables.update(result)

    return result

def send_request(data, variables):

    if not data: return

    url = global_context['endpoint']
    path = data['path'] if 'path' in data else ''
    body = data['body'] if 'body' in data else None
    method = data['method'] if 'method' in data else 'GET'

    # print("{} {}{}".format(method, url, path))

    if method == 'GET':
        r = requests.get(url + path, headers = jsonHeaders)
    if method == 'POST':
        r = requests.post(url + path, data = json.dumps(body), headers = jsonHeaders)

    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
        return

    result = json.loads(r.text)

    if 'result' in data:
        part = get_json_path(result ,data['result']['path'])

        partResult = {
            data['result']['name']: part
        }
        return partResult
    else:
        return result

def get_json_path(data, path):
    jsonpath_expr = parse(path)
    part = [match.value for match in jsonpath_expr.find(data)]
    if len(part) == 1:
        part = part[0]
    return part

#
# Variables task
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
# Variable resolving
#

def resolve_variables(item, variables):
    if not item:
        return
    if type(item) is str:
        return resolve_variables_in_string(item, variables)
    if type(item) is dict:
        return resolve_variables_in_dict(item, variables)
    if isinstance(item, list):
        return resolve_variables_in_list(item, variables)
    return item

def resolve_variables_in_string(text, variables):
    regex = r"^\$\{(.*)\}$"
    match = re.search(regex, text)
    if match:
        variable = match.group(1)
        if variable in variables:
            return variables[variable]
        else:
            # Do not reolve or warn unknown variables so foreach can do late binding.
            return text
    else:
        for key in variables:
            if type(variables[key]) is str:
                text = text.replace('${' + key + '}', variables[key])
        return text

def resolve_variables_in_dict(dict, variables):
    copy = {}
    for key in dict:
        copy[key] = resolve_variables(dict[key], variables)
    return copy

def resolve_variables_in_list(list, variables):
    copy = []
    for item in list:
        copy.append(resolve_variables(item, variables))
    return copy


#
# Printing tasks
#

def print_text(data, variables):
    print(data)

def print_json(data, variables):
    print_as_json(data)

#
# Foreach
#

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
# Util
#

jsonHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}

def print_as_json(dict):
    print(json.dumps(dict, indent=2, sort_keys=True))

def print_as_yaml(dict):
    print(yaml.dump(dict, default_flow_style=False))

def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()

def read_yaml_file(fileArgument, data = []):
    with open(fileArgument, 'r') as stream:
        for fileData in yaml.load_all(stream):
            data.append(fileData)
    return data

def add_from_yaml_file(fileArgument, data):
    if not os.path.isfile(fileArgument):
        return

    with open(fileArgument, 'r') as stream:
        for fileData in yaml.load_all(stream):
            data.update(fileData)

    return data

def read_yaml_files(fileArgument, data = []):

    if os.path.isdir(fileArgument):
        for root, subdirs, files in os.walk(fileArgument):
            for file in files:
                if file.endswith('.yaml'):
                    read_yaml_file(format(os.path.join(root, file)), data)
    else:
        # Read all items from one file
        read_yaml_file(fileArgument, data)

    return data




# Execute script
main()
