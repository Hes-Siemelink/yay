from yay import util

class TestJsonpath():

    data = {
        'one' : '1',
        'two' : '2',
        'nested': {
            'item': 'stuff'
        }
    }

    def test_json_path(self):
        result = util.get_json_path(self.data, 'one')
        assert result == '1'

    def test_json_path_with_dollar(self):
        result = util.get_json_path(self.data, '$.one')
        assert result == '1'

    def test_json_path_nested(self):
        result = util.get_json_path(self.data, '$.nested.item')
        assert result == 'stuff'
