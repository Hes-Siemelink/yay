import json
import yaml
import os


class YayException(Exception):
    pass


def format_json(dict):
    return json.dumps(dict, indent=2, sort_keys=False)


def print_as_json(dict):
    print(format_json(dict))


def format_yaml(dict):
    return yaml.dump(dict, default_flow_style=False, sort_keys=False)


def print_as_yaml(dict):
    print(format_yaml(dict))


def read_file(filename):
    with open(filename, 'r') as file:
        return file.read()


def read_yaml_file(fileArgument, data=None):
    if data == None:
        data = []

    with open(fileArgument, 'r') as stream:
        for fileData in yaml.load_all(stream, Loader=yaml.Loader):
            data.append(fileData)
    return data


def add_from_yaml_file(fileArgument, data):
    if not os.path.isfile(fileArgument):
        return

    with open(fileArgument, 'r') as stream:
        for fileData in yaml.load_all(stream, Loader=yaml.Loader):
            data.update(fileData)

    return data


def read_yaml_files(fileArgument, data=None):
    if data == None:
        data = []

    if os.path.isdir(fileArgument):
        for root, subdirs, files in os.walk(fileArgument):
            for file in files:
                if file.endswith('.yaml'):
                    read_yaml_file(format(os.path.join(root, file)), data)
    else:
        # Read all items from one file
        read_yaml_file(fileArgument, data)

    return data


def is_dict(item):
    return isinstance(item, dict)


def is_list(item):
    return isinstance(item, list)


def is_scalar(item):
    return isinstance(item, str)


class RawDict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)


class RawList(list):
    def __init__(self, *args, **kwargs):
        list.__init__(self, *args, **kwargs)


def is_raw(item):
    return isinstance(item, RawDict) or isinstance(item, RawList)


def raw(item):
    if is_list(item):
        return RawList(item)
    if is_dict(item):
        return RawDict(item)

    return item  # TODO handle strings


def live(item):
    if is_list(item):
        return list(item)
    if is_dict(item):
        return dict(item)

    return item  # TODO handle strings


def is_empty(item):
    if item is None: return True
    if is_scalar(item):
        if not item: return False
    return True


def as_list(item):
    if not is_list(item):
        return [item]
    return item


def dict_merge(context, profile):
    for key in profile:
        if key in context:
            context[key].update(profile[key])
        else:
            context[key] = profile[key]


def get_parameter(data, name, default=None):
    parameter = data.get(name)
    if parameter is None:
        parameter = default
    if parameter is None:
        raise YayException("Missing parameter '{}' in:\n{}".format(name, yaml.dump(data, default_flow_style=False)))
    return parameter
