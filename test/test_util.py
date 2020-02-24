import yay.vars
from yay import util

class TestJsonpath():

    data = {
        'one' : '1',
        'two' : '2',
        'nested': {
            'item': 'stuff'
        },
        'list': [1, 2, 3]
    }

    def test_json_path_with_dollar(self):
        result = yay.vars.get_json_path(self.data, '$.one')
        assert result == '1'

    def test_json_path_nested(self):
        result = yay.vars.get_json_path(self.data, '$.nested.item')
        assert result == 'stuff'

    def test_json_path_nested2(self):
        result = yay.vars.get_json_path(self.data, '$..item')
        assert result == 'stuff'

    def test_json_path_list(self):
        result = yay.vars.get_json_path(self.data, '$.list[0]')
        assert result == 1
