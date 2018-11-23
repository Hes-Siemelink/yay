import pytest
from yay.test import *

class TestCore():

    def test_process_task(self):
        task = {'Test':'something'}
        mock = get_test_mock()

        core.process_task(task)

        assert len(mock.invocations) == 1
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}


    def test_process_tasks(self):
        yaml = """
        Test: something
        ---
        Test: something else
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
        For each:
          item:
          - one
          - two
          - three
          Do:
            Test: ${item}
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
        Test: something
        ---
        Test: ${result}
        """)
        mock = get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result(self):
        tasks = from_yaml("""
        Test: something
        Set: test_outcome
        ---
        Test: ${test_outcome}
        """)
        mock = get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_long_form(self):
        tasks = from_yaml("""
        Test: something
        Set:
          test_outcome: ${result}
        ---
        Test: ${test_outcome}
        """)
        mock = get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_with_path(self):
        tasks = from_yaml("""
        Test:
          something: nested
        Set:
          test_outcome: ${result.something}
        ---
        Test: ${test_outcome}
        """)
        mock = get_test_mock()

        core.process_tasks(tasks, {})

        assert mock.invocations[1].data == 'nested'

    def test_change_result_part(self):
        tasks = from_yaml("""
        Test: 
          something: nested
        Set:
          result: ${result.something}
        ---
        Test: ${result}
        """)
        mock = get_test_mock()

        core.process_tasks(tasks, {})

        assert mock.invocations[1].data == 'nested'

    def test_assert(self):
        tasks = from_yaml("""
        Assert equals: 
          actual:   one
          expected: one
        """)

        core.process_tasks(tasks, {})

    def test_assertion_failure(self):
        tasks = from_yaml("""
        Assert equals: 
          actual:   one
          expected: two
        """)

        with pytest.raises(AssertionError):
            core.process_tasks(tasks, {})

    def test_multiple_invocations_with_list(self):
        tasks = from_yaml("""
        Test: 
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
        Do:
        - Test: something 
        - Test: again 
        """)
        mock = get_test_mock()

        variables = {}
        core.process_tasks(tasks, variables)

        assert len(mock.invocations) == 2
        assert variables['result'] == 'again'




