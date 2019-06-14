import time

from yay.core import register, noop
from yay.util import *

#
# Join and merge
#

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
    output = None

    for item in data:

        if first:
            if is_dict(item):
                output = item
            else:
                output = as_list(item)
            first = False
            continue

        if is_dict(item):
            output.update(item)
        else:
            output.extend(as_list(item))

    return output

#
# Replace
#

def replace_text(data, variables):
    part = get_parameter(data, 'part')
    text = get_parameter(data, 'in')
    replacement = get_parameter(data, 'with')

    return text.replace(part, replacement)

#
# Wait
#

def wait(data, variables):
    time.sleep(data)
#
# Printing
#

def print_text(data, variables):
    print(data)

def print_json(data, variables):
    print_as_json(data)

def print_yaml(data, variables):
    print_as_yaml(data)

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
register('Wait',  wait)
