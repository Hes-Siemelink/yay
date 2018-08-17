from yppy import util

class TestJsonpath():

    data = {
        "one" : "1",
        "two" : "2"
    }

    def test_json_path(self):
        result = util.get_json_path(self.data, "one")
        assert result == "1"

    def test_json_path_with_dollar(self):
        result = util.get_json_path(self.data, "$.one")
        assert result == "1"
