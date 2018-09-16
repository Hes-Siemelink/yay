from yay import core

from yay.util import *

def write_file(data, variables):
    name = get_parameter(data, 'name')
    content = get_parameter(data, 'content')

    with open(name, 'w') as file:
        file.write(format_yaml(content))

# Register tasks
core.register('Write file', write_file)
