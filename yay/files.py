from yay import core

from yay.util import *

def write_file(data, variables):
    name = get_parameter(data, 'name')
    content = get_parameter(data, 'contents') # See https://english.stackexchange.com/questions/56831/file-content-vs-file-contents

    with open(name, 'w') as file:
        file.write(format_yaml(content))

def read_file(data, variables):
    contents = read_yaml_file(data)
    if len(contents) == 1:
        return contents[0]
    return contents

# Register tasks
core.register('Write file', write_file)
core.register('Read file', read_file)
