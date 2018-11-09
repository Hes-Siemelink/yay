import pytest
import time

from yay.test import *
from yay import script
from yay import http
from yay import test_server

yay_test_files = get_files('../test/yay')

@pytest.fixture(scope="session", autouse=True)
def setup_test_server():
    test_server.start()
    # Wait for HTTP server startup
    time.sleep(0.1)

@pytest.mark.parametrize("file", yay_test_files)
def test_yay(file):
    run_yay_test(file)