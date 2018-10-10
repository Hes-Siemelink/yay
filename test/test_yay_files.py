import pytest
from yay.test import *

from yay import script

yay_test_files = get_files('../test/resources')

@pytest.mark.parametrize("file", yay_test_files)
def test_yay_files(file):
    run_yay_test(file)