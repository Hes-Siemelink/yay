from collections import namedtuple
import yaml
import pytest
import textwrap

from yay import core
from yay import util


class TestVariableResolution():

    def get_test_mock(self):
        mock = MockTask()
        core.register('test', mock.invoke)
        return mock


    def test_process_task(self):
        task = {'test':'something'}
        mock = self.get_test_mock()

        core.process_task(task)

        assert len(mock.invocations) == 1
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}


    def test_process_tasks(self):
        yaml = """
        test: something
        ---
        test: something else
        """
        tasks = from_yaml(yaml)
        mock = self.get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}
        assert mock.invocations[1].data == 'something else'
        assert mock.invocations[0].variables == {}


    def test_for_each(self):
        tasks = from_yaml("""
        foreach:
            var: item
            in:
            - one
            - two
            - three
            test: ${item}
        """)
        mock = self.get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 3
        assert mock.invocations[0].data == 'one'
        assert mock.invocations[0].variables == {'item' : 'one'}
        assert mock.invocations[1].data == 'two'
        assert mock.invocations[1].variables == {'item' : 'two'}
        assert mock.invocations[2].data == 'three'
        assert mock.invocations[2].variables == {'item' : 'three'}

#
# Test util
#

def from_yaml(text):
    return list(yaml.load_all(textwrap.dedent(text)))

Invocation = namedtuple('Invocation', ['data', 'variables'])
class MockTask:
    def __init__(self):
        self.invocations = []

    def invoke(self, data, variables):
        self.invocations.append(Invocation(data, variables.copy()))
