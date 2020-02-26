from yay.context import command_handler


@command_handler('Python')
def execute_python_script(data, context):
    exec(data, context.variables)
