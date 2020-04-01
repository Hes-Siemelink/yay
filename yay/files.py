from yay.runtime import command_handler
from yay.util import *


@command_handler('Write file')
def write_file(data, context):
    name = get_parameter(data, 'name')
    content = get_parameter(data, 'contents')  # See https://english.stackexchange.com/questions/56831/file-content-vs-file-contents

    with open(name, 'w') as file:
        file.write(format_yaml(content))


@command_handler('Read file')
def read_file(data, context):
    contents = read_yaml_file(data)
    if len(contents) == 1:
        return raw(contents[0])
    return raw(contents)
