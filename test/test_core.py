import pytest
from yay.test import *

class TestCore():

    def test_process_task(self):
        mock = get_test_mock()

        execution.process_task({'Test': 'something'})

        assert len(mock.invocations) == 1
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}


    def test_process_tasks(self):
        mock = get_test_mock()

        run('''
        Test: something
        ---
        Test: something else
        ''')

        assert len(mock.invocations) == 2
        assert mock.invocations[0].data == 'something'
        assert mock.invocations[0].variables == {}
        assert mock.invocations[1].data == 'something else'
        assert mock.invocations[0].variables == {}


    def test_for_each(self):
        mock = get_test_mock()

        run('''
        For each:
          item:
          - one
          - two
          - three
          Do:
            Test: ${item}
        ''')

        assert len(mock.invocations) == 3
        assert mock.invocations[0].data == 'one'
        assert mock.invocations[0].variables['item'] == 'one'
        assert mock.invocations[1].data == 'two'
        assert mock.invocations[1].variables['item'] == 'two'
        assert mock.invocations[2].data == 'three'
        assert mock.invocations[2].variables['item'] == 'three'

    def test_pipe_result(self):
        mock = get_test_mock()

        run('''
        Test: something
        ---
        Test: ${result}
        ''')

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result(self):
        mock = get_test_mock()

        run('''
        Test: something
        Set: test_outcome
        ---
        Test: ${test_outcome}
        ''')

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_long_form(self):
        mock = get_test_mock()

        run('''
        Test: something
        Set:
          test_outcome: ${result}
        ---
        Test: ${test_outcome}
        ''')

        assert len(mock.invocations) == 2
        assert mock.invocations[1].data == 'something'

    def test_store_result_with_path(self):
        mock = get_test_mock()

        run('''
        Test:
          something: nested
        Set:
          test_outcome: ${result.something}
        ---
        Test: ${test_outcome}
        ''')

        assert mock.invocations[1].data == 'nested'

    def test_change_result_part(self):
        mock = get_test_mock()

        run('''
        Test: 
          something: nested
        Set:
          result: ${result.something}
        ---
        Test: ${result}
        ''')

        assert mock.invocations[1].data == 'nested'

    def test_assert(self):
        run('''
        Assert equals: 
          actual:   one
          expected: one
        ''')

    def test_assertion_failure(self):
        with pytest.raises(AssertionError):
            execution.process_script(from_yaml('''
            Assert equals: 
              actual:   one
              expected: two
            '''), {})

    def test_multiple_invocations_with_list(self):
        mock = get_test_mock()

        variables = {}
        run('''
        Test: 
        - something
        - again
        ''', variables)

        assert len(mock.invocations) == 2
        assert variables['result'] == ['something', 'again']

    def test_do(self):
        mock = get_test_mock()

        variables = {}
        run('''
        Do:
        - Test: something 
        - Test: again 
        ''', variables)

        assert len(mock.invocations) == 2
        assert variables['result'] == ['something', 'again']


def run(yay_script_in_yaml, variables = {}):
    execution.process_script(from_yaml(yay_script_in_yaml), variables)

