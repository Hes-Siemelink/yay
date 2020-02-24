from yay.core import command_handler
from yay.util import *
from subprocess import call
import os
import tempfile

@command_handler('XL apply')
def xl_apply(data, variables):

    file, path = tempfile.mkstemp()
    try:
        with os.fdopen(file, 'w') as tmp:
            tmp.write(format_yaml(data))
        command = "xl apply -f {}".format(path)
        call(command, shell=True)
    finally:
        os.remove(path)

