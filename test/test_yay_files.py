import pytest

from yay.test import *
from yay import __main__

@pytest.fixture(scope="session", autouse=True)
def setup_test_server():

    # Start server
    from yay import test_server
    test_server.start()

    # Wait for HTTP server startup
    import time
    time.sleep(0.1)


@pytest.mark.parametrize("file", get_files('yay', __file__))
def test_yay(file):
    basePath = os.path.dirname(os.path.realpath(file))
    core.register_scripts(basePath)

    run_yay_test(file)