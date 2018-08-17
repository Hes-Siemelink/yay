#
# Variable resolving
#
import re
from yppy import util

varSyntax = r"\$\{(.*?)\}"

def resolve_variables(item, variables):
    if not item:
        return
    if type(item) is str:
        return resolve_variables_in_string(item, variables)
    if type(item) is dict:
        return resolve_variables_in_dict(item, variables)
    if isinstance(item, list):
        return resolve_variables_in_list(item, variables)
    return item

def resolve_variables_in_string(text, variables):
    regex = r"^\$\{(.*)\}$"
    match = re.search(regex, text)
    if match:
        variable = match.group(0)
        return get_value_with_path(variable, variables)
    else:
        variablesInText = set(re.findall(r"\$\{.*?\}", text))
        for variable in variablesInText:
            value = get_value_with_path(variable, variables)
            if value:
                text = text.replace(variable, value)
        return text

def resolve_variables_in_dict(dict, variables):
    copy = {}
    for key in dict:
        copy[key] = resolve_variables(dict[key], variables)
    return copy

def resolve_variables_in_list(list, variables):
    copy = []
    for item in list:
        copy.append(resolve_variables(item, variables))
    return copy

def get_value_with_path(variable, variables):
    var = variable
    match = re.search(varSyntax, var)
    if match:
        var = match.group(1)

    path = None
    pathSyntax = r"^(.*)\.(.*)$"
    match = re.search(pathSyntax, var)
    if match:
        var = match.group(1)
        path = match.group(2)

    if var in variables:
        value = variables[var]
        return util.get_json_path(value, path)
    else:
        # Do not reolve or warn about unknown variables so foreach can do late binding.
        return variable
