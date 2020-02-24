#
# Test util
#

from collections import namedtuple
import os
import textwrap
import yaml

from yay import execution

Invocation = namedtuple('Invocation', ['data', 'variables'])
class MockTask:
    def __init__(self):
        self.invocations = []

    def invoke(self, data, variables):
        self.invocations.append(Invocation(data, variables.copy()))
        return data

def get_test_mock():
    mock = MockTask()
    execution.register('Test', mock.invoke)
    return mock

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


def run_yay_test(file, variables):
    script = from_file(file)

    execution.process_script(script, variables)

