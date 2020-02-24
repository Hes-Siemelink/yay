from yay.context import command_handler


@command_handler('Python')
def execute_python_script(data, variables):
    exec(data, variables)
