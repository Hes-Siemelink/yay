#
# Test util
#

import yaml
import textwrap
import os
from collections import namedtuple

from yay import core

Invocation = namedtuple('Invocation', ['data', 'variables'])
class MockTask:
    def __init__(self):
        self.invocations = []

    def invoke(self, data, variables):
        self.invocations.append(Invocation(data, variables.copy()))
        return data

def get_test_mock():
    mock = MockTask()
    core.register('Test', mock.invoke)
    return mock

def from_yaml(text):
    return list(yaml.load_all(textwrap.dedent(text)))

def get_files(testDir):
    basePath = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(basePath, testDir)
    print(path)
    files = []
    for file in os.listdir(path):
        if file.endswith('.yay'):
            files.append(os.path.join(path, file))
    return files

def from_yaml(text):
    return list(yaml.load_all(textwrap.dedent(text)))

def from_file(file):
    with open (file, "r") as myfile:
        data = myfile.read()
    return from_yaml(data)


def run_yay_test(file):
    tasks = from_file(file)

    variables = {}
    core.process_tasks(tasks, variables)

