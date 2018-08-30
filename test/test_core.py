from collections import namedtuple
import yaml
import textwrap

from yay import core

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
        assert mock.invocations[0].variables['item'] == 'one'
        assert mock.invocations[1].data == 'two'
        assert mock.invocations[1].variables['item'] == 'two'
        assert mock.invocations[2].data == 'three'
        assert mock.invocations[2].variables['item'] == 'three'

    def test_pipe_result(self):
        tasks = from_yaml("""
        test: something
        ---
        test: ${result}
        """)
        mock = self.get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result(self):
        tasks = from_yaml("""
        test: something
        set: test_outcome
        ---
        test: ${test_outcome}
        """)
        mock = self.get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_long_form(self):
        tasks = from_yaml("""
        test: something
        set:
            test_outcome: ${result}
        ---
        test: ${test_outcome}
        """)
        mock = self.get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_with_path(self):
        tasks = from_yaml("""
        test:
            something: nested
        set:
            test_outcome: ${result.something}
        ---
        test: ${test_outcome}
        """)
        mock = self.get_test_mock()

        core.process_tasks(tasks, {})

        assert mock.invocations[1].data == 'nested'

    def test_change_result_part(self):
        tasks = from_yaml("""
        test: 
            something: nested
        set:
            result: ${result.something}
        ---
        test: ${result}
        """)
        mock = self.get_test_mock()

        core.process_tasks(tasks, {})

        assert mock.invocations[1].data == 'nested'

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
        return data
