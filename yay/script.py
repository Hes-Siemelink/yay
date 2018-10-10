from yay import core

from yay.util import *

def execute_python_script(data, variables):
    exec(data, variables)


# Register tasks
core.register('Python', execute_python_script)
