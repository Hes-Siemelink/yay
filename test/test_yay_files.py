import pytest

from yay.context import YayContext, defaultContext
from yay.test import *

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

    context = YayContext(defaultContext)
    context.apply_directory_context(script_dir, profile='test')
    context.run_script(from_file(file))
