#
# Test util
#

from collections import namedtuple
import os
import textwrap
import yaml

from yay.context import YayContext

Invocation = namedtuple('Invocation', ['data', 'variables'])
class MockHandler:
    def __init__(self):
        self.invocations = []

    def invoke(self, data, context):
        self.invocations.append(Invocation(data, context.variables.copy()))
        return data

def run_script(yay_script_in_yaml, variables, mock = None):
    context = YayContext()
    context.runner.variables = variables
    if mock:
        context.add_command_handler('Test', mock.invoke)

    context.run_script(from_yaml(yay_script_in_yaml))

def from_yaml(text):
    return list(yaml.load_all(textwrap.dedent(text), Loader=yaml.Loader))

def get_files(testDir, base=None):
    if not base:
        base = __file__
    basePath = os.path.dirname(os.path.realpath(base))
    path = os.path.join(basePath, testDir)
    path = os.path.relpath(path)

    files = []
    setup_file = None
    teardown_file = None
    for file in os.listdir(path):
        if file.endswith('.yay'):
            file_with_path = os.path.join(path, file)
            if 'setup.yay' == file:
                setup_file = file_with_path
            elif 'teardown.yay' == file:
                teardown_file = file_with_path
            else:
                files.append(file_with_path)

    if setup_file:
        files.insert(0, setup_file)
    if teardown_file:
        files.append(teardown_file)

    return files

def from_yaml(text):
    return list(yaml.load_all(textwrap.dedent(text), Loader=yaml.Loader))

def from_file(file):
    with open (file, "r") as myfile:
        data = myfile.read()
    return from_yaml(data)

