import json
import yaml
import os

from jsonpath_rw import jsonpath, parse

def get_json_path(data, path):
    if not path:
        return data

    jsonpath_expr = parse(path)
    part = [match.value for match in jsonpath_expr.find(data)]
    if len(part) == 0:
        return None
    if len(part) == 1:
        part = part[0]
    return part

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
