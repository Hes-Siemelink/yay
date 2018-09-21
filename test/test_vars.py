from yay import vars

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
        },
        'list' : [0, 1, 2],
        'a': 'Would like to be ${one}',
        'b': 'Would like to be ${b}'
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

    def test_resolve_unknow_json_path(self):
        input = '${dict.unknown}'

        result = vars.resolve_variables(input, self.variables)

        assert result == input

    def test_resolve_json_path_index(self):
        input = '${list[0]}'

        result = vars.resolve_variables(input, self.variables)

        assert result == 0

    def test_resolve_another_variable(self):
        input = '${a}'

        result = vars.resolve_variables(input, self.variables)

        assert result == 'Would like to be 1'

    def test_resolve_two_variablea(self):
        input = '${one}${two}'

        result = vars.resolve_variables(input, self.variables)

        assert result == '12'

    # def test_resolve_recursive(self):
    #     input = '${b}'
    #
    #     result = vars.resolve_variables(input, self.variables)
    #
    #     assert result == 'Would like to be ${b}'
