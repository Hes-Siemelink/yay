#
# Variable resolving
#
import re

from yay.util import *


class VariableMatcher:
    VARIABLE_REGEX = r'\$\{([^\}]+)\}'
    ONE_VARIABLE_ONLY_REGEX = r'^' + VARIABLE_REGEX + '$'

def resolve_variables(item, variables):
    if not item:
        return item
    if is_scalar(item):
        return resolve_variables_in_string(item, variables)
    if is_dict(item):
        return resolve_variables_in_dict(item, variables)
    if is_list(item):
        return resolve_variables_in_list(item, variables)
    return item

def resolve_variables_in_string(text, variables):
    match = re.search(VariableMatcher.ONE_VARIABLE_ONLY_REGEX, text)
    if match:
        variable = match.group(1)
        return get_value_with_path(variable, variables)
    else:
        variablesInText = set(re.findall(VariableMatcher.VARIABLE_REGEX, text))
        for variable in variablesInText:
            value = get_value_with_path(variable, variables)
            if not value is None:
                if is_dict(value) or is_list(value):
                    value = format_yaml(value).strip()
                text = text.replace(in_var_syntax(variable), value)
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

    # Check if we have a JSON path syntax and split variable into root and path component
    (var, path) = split_jsonpath(variable)

    # Do not resolve or warn about unknown variables so foreach can do late binding.
    if not var in variables:
        return in_var_syntax(variable)

    value = variables[var]

    if path:
        part = get_json_path(value, path)
        if part == None:
            # unknown JSON path
            return in_var_syntax(variable)
        else:
            return resolve_variables(part, var)
    else:
        return resolve_variables(value, variables)

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

def in_var_syntax(variable):
    return '${' + variable + '}'
