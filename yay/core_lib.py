import time

from yay.core import command_handler, OUTPUT_VARIABLE
from yay.util import *
from yay import vars

#
# Meta info
#

@command_handler('Name')
@command_handler('Task')
@command_handler('Test case')
def noop(data, variables):
    pass

#
# Join and merge
#

@command_handler('Join')
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

@command_handler('Merge', list_processor=True)
def merge(data, variables):

    if is_dict(data):
        merge([variables[OUTPUT_VARIABLE], data], variables)
        return

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

@command_handler('Apply variables')
def apply_variables(data, variables):
    return raw(vars.resolve_variables(live(data), variables))

#
# Replace
#

@command_handler('Replace')
def replace_text(data, variables):
    part = get_parameter(data, 'part')
    text = get_parameter(data, 'in')
    replacement = get_parameter(data, 'with')

    return text.replace(part, replacement)

#
# Wait
#

@command_handler('Wait')
def wait(data, variables):
    time.sleep(data)

#
# Printing
#

@command_handler('Print')
def print_text(data, variables):
    print(data)

@command_handler('Print JSON')
@command_handler('Print as JSON')
def print_json(data, variables):
    print_as_json(data)

@command_handler('Print YAML')
@command_handler('Print as YAML')
def print_yaml(data, variables):
    print_as_yaml(data)
