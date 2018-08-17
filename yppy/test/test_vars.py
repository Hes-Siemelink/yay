from yppy import vars
from yppy import util

import pytest

class TestVariableResolution():

    variables = {
        'one' : '1',
        'two' : '2',
        'dict': {
            'entry': 'value',
            'nested': {
                'item': 'stuff'
            }
        }
    }


    def test_resolve_variables_in_string(self):
        input = "Count from ${one} to ${two}."

        result = vars.resolve_variables_in_string(input, self.variables)

        assert result == "Count from 1 to 2."


    def test_resolve_single_variable_in_string(self):
        input = '${one}'

        result = vars.resolve_variables_in_string(input, self.variables)

        assert result == '1'


    def test_resolve_single_variable(self):
        input = '${one}'

        result = vars.resolve_variables(input, self.variables)

        assert result == '1'


    def test_resolve_variable_in_dict(self):
        input = {
            'entry': '${one}'
        }

        result = vars.resolve_variables(input, self.variables)

        assert type(result) is dict
        assert 'entry' in result
        assert result['entry'] == '1'


    def test_resolve_dict_from_string(self):
        input = '${dict}'

        result = vars.resolve_variables(input, self.variables)

        assert type(result) is dict
        assert result['entry'] == 'value'


    def test_resolve_in_list(self):
        input = [0, 'one', '${two}', '${dict}']

        result = vars.resolve_variables(input, self.variables)

        assert isinstance(result, list)
        assert len(result) == 4
        assert result[0] == 0
        assert result[1] == 'one'
        assert result[2] == '2'
        assert type(result[3]) is dict
        assert result[3]['entry'] == 'value'

    def test_resolve_json_path(self):
        input = 'My ${dict.entry}'

        result = vars.resolve_variables(input, self.variables)

        assert result == 'My value'

    def test_resolve_json_path_nested(self):
        input = 'My ${dict.nested.item}'

        result = vars.resolve_variables(input, self.variables)

        assert result == 'My stuff'

    #
    # Not implemented yet
    #

    @pytest.mark.skip(reason="Referring to a dict inside a string with more content is not defined.")
    def test_resolve_dict_from_string_embedded(self):
        result = vars.resolve_variables('I have ${dict}', self.variables)

        print(result)
