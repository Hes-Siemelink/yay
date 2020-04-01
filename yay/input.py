from yay.runtime import command_handler
from yay.vars import OUTPUT_VARIABLE
from PyInquirer import prompt


@command_handler('User Input')
def ask_user(data, context):
    if 'name' not in data:
        data['name'] = OUTPUT_VARIABLE

    answers = prompt([data])
    context.variables.update(answers)


@command_handler('Check Input')
def check_input(data, context):
    for variable in data:
        if variable in context.variables:
            continue

        query = {
            'type': 'input',
            'message': data[variable] + f' (${{{variable}}}):',
            'name': variable
        }
        answers = prompt([query])
        context.variables.update(answers)
