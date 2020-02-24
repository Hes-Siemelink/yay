from yay.context import command_handler
from PyInquirer import prompt

@command_handler('User Input')
def ask_user(data, variables):
    if 'name' not in data:
        data['name'] = core.OUTPUT_VARIABLE

    answers = prompt([data])
    variables.update(answers)

@command_handler('Check Input')
def check_input(data, variables):

    for variable in data:
        if variable in variables:
            continue

        query = {
            'type': 'input',
            'message': data[variable] + f' (${{{variable}}}):',
            'name': variable
        }
        answers = prompt([query])
        variables.update(answers)
