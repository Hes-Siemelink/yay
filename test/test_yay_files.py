import pytest

import yay.context
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
    script_dir = os.path.dirname(os.path.realpath(file))
    execution.register_scripts(script_dir)
    context = yay.context.get_context(script_dir, 'test')

    run_yay_test(file, context)