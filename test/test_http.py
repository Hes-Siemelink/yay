import pytest
import time

from yay import http
from yay import test_server
from yay.test import *

class TestHttp():

    @pytest.fixture(scope="session", autouse=True)
    def setup_test_server(cls):
        test_server.start()
        # Wait for HTTP server startup
        time.sleep(0.1)

    def test_process_tasks(self):
        yaml = """
        Http GET:
          url: http://localhost:5000
          path: /users
        Test: ${result}
        """
        tasks = from_yaml(yaml)
        mock = get_test_mock()

        core.process_tasks(tasks)

        assert len(mock.invocations) == 1
        assert mock.invocations[0].data == [1, 2, 3]


