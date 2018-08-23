#
# Variable resolving
#
import re

from yay import util

varSyntax = r"\$\{(.*?)\}"

def resolve_variables(item, variables):
    if not item:
        return item
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

    # Check if we have a JSON path syntax and split variable into root and path component
    (var, path) = split_jsonpath(var)

    # Do not resolve or warn about unknown variables so foreach can do late binding.
    if not var in variables:
        return variable

    value = variables[var]

    if path:
        part = util.get_json_path(value, path)
        if not part == None:
            return part
        else:
            return variable
    else:
        return value

def split_jsonpath(var):
    PATH_SYNTAX  = r"^(.*?)\.(.*)$"
    INDEX_SYNTAX = r"^(.*?)(\[.*)$"
    (var, path) = match_two_groups(var, PATH_SYNTAX)
    if not path:
        (var, path) = match_two_groups(var, INDEX_SYNTAX)

    return (var, path)

def match_two_groups(text, regex):
    match = re.search(regex, text)
    if match:
        return (match.group(1), match.group(2))
    else:
        return (text, None)
