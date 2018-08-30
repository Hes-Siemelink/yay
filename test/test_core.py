from collections import namedtuple
import yaml
import textwrap
import os
import pytest

from yay import core

class TestVariableResolution():

    def test_process_task(self):
        task = {'test':'something'}
        mock = get_test_mock()

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
        mock = get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}
        assert mock.invocations[1].data == 'something else'
        assert mock.invocations[0].variables == {}


    def test_for_each(self):
        tasks = from_yaml("""
        foreach:
            item:
            - one
            - two
            - three
            do:
              test: ${item}
        """)
        mock = get_test_mock()

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
        mock = get_test_mock()

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
        mock = get_test_mock()

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
        mock = get_test_mock()

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
        mock = get_test_mock()

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
        mock = get_test_mock()

        core.process_tasks(tasks, {})

        assert mock.invocations[1].data == 'nested'

    def test_assert(self):
        tasks = from_yaml("""
        assert equals: 
          actual:   one
          expected: one
        """)

        core.process_tasks(tasks, {})

    def test_assertion_failure(self):
        tasks = from_yaml("""
        assert equals: 
          actual:   one
          expected: two
        """)

        with pytest.raises(AssertionError):
            core.process_tasks(tasks, {})

    def test_store_multiple_variables_from_result(self):
        run_yay_test('resources/store_multiple_variables_from_result.yaml')

    def test_multiple_invocations_with_list(self):
        tasks = from_yaml("""
        test: 
        - something
        - again
        """)
        mock = get_test_mock()

        variables = {}
        core.process_tasks(tasks, variables)

        assert len(mock.invocations) == 2
        assert variables['result'] == 'again'

    def test_do(self):
        tasks = from_yaml("""
        do:
        - test: something 
        - test: again 
        """)
        mock = get_test_mock()

        variables = {}
        core.process_tasks(tasks, variables)

        assert len(mock.invocations) == 2
        assert variables['result'] == 'again'

    def test_join(self):
        run_yay_test('resources/test_join.yaml')


#
# Test util
#

Invocation = namedtuple('Invocation', ['data', 'variables'])
class MockTask:
    def __init__(self):
        self.invocations = []

    def invoke(self, data, variables):
        self.invocations.append(Invocation(data, variables.copy()))
        return data

def get_test_mock():
    mock = MockTask()
    core.register('test', mock.invoke)
    return mock

def from_yaml(text):
    return list(yaml.load_all(textwrap.dedent(text)))

def from_file(file):
    path = dir_path = os.path.dirname(os.path.realpath(__file__))
    file = os.path.join(path, file)
    with open (file, "r") as myfile:
        data = myfile.read()
    return from_yaml(data)

def run_yay_test(file):
    tasks = from_file(file)
    mock = get_test_mock()

    variables = {}
    core.process_tasks(tasks, variables)
