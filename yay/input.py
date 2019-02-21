from yay import core
from yay.util import *
from PyInquirer import prompt

def ask_user(data, variables):
    if 'name' not in data:
        data['name'] = core.RESULT_VARIABLE

    answers = prompt([data])
    variables.update(answers)

def check_input(data, variables):

    for variable in data:
        if variable in variables:
            continue

        query = {
            'type': 'input',
            'message': data[variable] + f' ({variable}):',
            'name': variable
        }
        answers = prompt([query])
        variables.update(answers)


# Register command handlers
core.register('User Input', ask_user)
core.register('Input', check_input)