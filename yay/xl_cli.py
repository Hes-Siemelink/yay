from yay import core
from yay.util import *
from subprocess import call
import os
import tempfile

def xl_apply(data, variables):

    file, path = tempfile.mkstemp()
    try:
        with os.fdopen(file, 'w') as tmp:
            tmp.write(format_yaml(data))
            print(path)
            command = "xl apply -f {}".format(path)
            call(command, shell=True)
    finally:
        os.remove(path)

# Register tasks
core.register('XL apply', xl_apply)