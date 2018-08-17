from yppy import vars

class TestJsonpath():

    variables = {
        "one" : "1",
        "two" : "2"
    }


    def test_resolve_variables_in_string(self):
        result = vars.resolve_variables_in_string("Count from ${one} to ${two}.", self.variables)

        assert result == "Count from 1 to 2."
