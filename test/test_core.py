import pytest

from yay.test import *
from yay.context import runtime, YayContext

class TestCore():

    def test_process_task(self):
        mock = MockTask()
        runtime.add_command_handler('Test', mock.invoke)

        runtime.run_task({'Test': 'something'}, YayContext())

        assert len(mock.invocations) == 1
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}


    def test_process_tasks(self):
        mock = MockTask()

        run_script('''
        Test: something
        ---
        Test: something else
        ''', {}, mock)

        assert len(mock.invocations) == 2
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}
        assert mock.invocations[1].data == 'something else'
        assert mock.invocations[0].variables == {}


    def test_for_each(self):
        mock = MockTask()

        run_script('''
        For each:
          item:
          - one
          - two
          - three
          Do:
            Test: ${item}
        ''', {}, mock)

        assert len(mock.invocations) == 3
        assert mock.invocations[0].data == 'one'
        assert mock.invocations[0].variables['item'] == 'one'
        assert mock.invocations[1].data == 'two'
        assert mock.invocations[1].variables['item'] == 'two'
        assert mock.invocations[2].data == 'three'
        assert mock.invocations[2].variables['item'] == 'three'

    def test_pipe_result(self):
        mock = MockTask()

        run_script('''
        Test: something
        ---
        Test: ${result}
        ''', {}, mock)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result(self):
        mock = MockTask()

        run_script('''
        Test: something
        Set: test_outcome
        ---
        Test: ${test_outcome}
        ''', {}, mock)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_long_form(self):
        mock = MockTask()

        run_script('''
        Test: something
        Set:
          test_outcome: ${result}
        ---
        Test: ${test_outcome}
        ''', {}, mock)

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_with_path(self):
        mock = MockTask()

        run_script('''
        Test:
          something: nested
        Set:
          test_outcome: ${result.something}
        ---
        Test: ${test_outcome}
        ''', {}, mock)

        assert mock.invocations[1].data == 'nested'

    def test_change_result_part(self):
        mock = MockTask()

        run_script('''
        Test: 
          something: nested
        Set:
          result: ${result.something}
        ---
        Test: ${result}
        ''', {}, mock)

        assert mock.invocations[1].data == 'nested'

    def test_assert(self):
        run_script('''
        Assert equals: 
          actual:   one
          expected: one
        ''', {})

    def test_assertion_failure(self):
        with pytest.raises(AssertionError):
            runtime.run_script(from_yaml('''
            Assert equals: 
              actual:   one
              expected: two
            '''), YayContext())

    def test_multiple_invocations_with_list(self):
        mock = MockTask()

        variables = {}
        run_script('''
        Test: 
        - something
        - again
        ''', variables, mock)

        assert len(mock.invocations) == 2
        assert variables['result'] == ['something', 'again']

    def test_do(self):
        mock = MockTask()

        variables = {}
        run_script('''
        Do:
        - Test: something 
        - Test: again 
        ''', variables, mock)

        assert len(mock.invocations) == 2
        assert variables['result'] == ['something', 'again']



