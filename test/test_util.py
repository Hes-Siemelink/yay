from yay import util


class TestEscaping():

    def test_escape_dollar_curly(self):
        text = "Do my ${thing}"

        escaped_text = util.escape(text)

        assert escaped_text == "Do my $-{thing}"

    def test_escape_escaped(self):
        text = "Do the $---{dash}"

        escaped_text = util.escape(text)

        assert escaped_text == "Do the $----{dash}"

    def test_unescape_dollar_curly(self):
        text = "Do my $-{thing}"

        escaped_text = util.unescape(text)

        assert escaped_text == "Do my ${thing}"

    def test_unescape_escaped(self):
        text = "Do the $----{dash}"

        escaped_text = util.unescape(text)

        assert escaped_text == "Do the $---{dash}"
