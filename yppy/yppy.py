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
    handlers['variables'] = process_variables
    handlers['request'] = process_request
    handlers['print_json'] = print_json

    # Read YAML files
    tasks = read_yaml_files(fileArgument)

    # Process all
    process_tasks(tasks, endpoint)

def process_tasks(tasks, endpoint, variables = {}):
    separator = False
    for task in tasks:
        if separator:
            print("- - - - - - - - - - - - ")
        else:
            separator = True

        for type in handlers:
            if type in task:
                last_result = handlers[type](task[type], variables)

    if last_result: print_as_json(last_result)

#
# Requests
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
    path = resolve_variables_in_string(path, variables)
    body = data['body'] if 'body' in data else None
    body = resolve_variables(body, variables)
    method = data['method'] if 'method' in data else 'GET'

    print("{} {}{}".format(method, url, path))

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
        jsonpath_expr = parse(data['result']['path'])
        part = [match.value for match in jsonpath_expr.find(result)]
        if len(part) == 1:
            part = part[0]
        partResult = {
            data['result']['name']: part
        }
        return partResult
    else:
        return result

#
# Variables
#

def process_variables(item, variables):
    if not item: return

    for variable in item:
        content = None
        if 'merge' in variable:
            content = merge_content(variable['merge'], variables)
        name = variable['name']
        variables[name] = content

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
        return variables[variable]
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

def merge_content(mergeList, variables):
    content = None
    for mergeItem in mergeList:
        mergeItem = resolve_variables(mergeItem, variables)
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

def print_json(data, variables):
    data = resolve_variables(data, variables)
    print_as_json(data)

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
            fileData['$location'] = fileArgument
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
