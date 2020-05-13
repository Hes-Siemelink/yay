import copy

from yay.runtime import command_handler


@command_handler('Python')
def execute_python_script(data, context):

    # Put variables in context
    python_context = copy.deepcopy(context.variables)

    # Run Python script
    exec(data, python_context)

    # Update variables with Python context
    for key in context.variables:
        if key in python_context:
            context.variables[key] = python_context[key]
    output = python_context.get('output')
    if output:
        context.variables['output'] = output
