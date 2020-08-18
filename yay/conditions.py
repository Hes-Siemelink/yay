from yay.util import *


def pop_conditions(data):
    condition_keys = ['object','equals', 'in', 'all', 'any', 'not']
    conditions = {key: data.pop(key) for key in condition_keys if key in data}
    return conditions

def parse_condition(data):

    if 'object' in data:
        object = data['object']

        if 'equals' in data:
            return Equals(object, data['equals'])

        if 'in' in data:
            return Contains(object, data['in'])

        raise YayException("Condition with 'object' should have either 'equals' or 'in'.")

    elif 'all' in data:
        all = data['all']
        expressions = [parse_condition(condition) for condition in all]
        return All(expressions)

    elif 'any' in data:
        any = data['any']
        expressions = [parse_condition(condition) for condition in any]
        return Any(expressions)

    elif 'not' in data:
        not_expression = data['not']
        expression = parse_condition(not_expression)
        return Not(expression)

    else:
        raise YayException("Condition needs 'object', 'all', 'any' or 'not'.")

    return condition

class Equals():

    def __init__(self, object, equals):
        self.object = object
        self.equals = equals

    def is_true(self):
        return self.object == self.equals

    def __repr__(self):
        return f"{self.object} == {self.equals}"

    def as_dict(self):
        dict = {'object': as_dict(self.object), 'equals': as_dict(self.equals)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict


class Contains():

    def __init__(self, object, list):
        self.object = object
        self.list = list

    def is_true(self):
        if is_dict(self.object) and is_dict(self.list):
            return contains_all(self.object, self.list)
        else:
            return self.object in self.list

    def __repr__(self):
        return f"{self.object} in {self.list}"

    def as_dict(self):
        dict = {'object': as_dict(self.object), 'in': as_dict(self.list)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict

def contains_all(subset, superset):
    for key in subset:
        if key not in superset:
            return False
        if subset[key] != superset[key]:
            return False
    return True

class All():

    def __init__(self, expressions):
        self.expressions = expressions

    def is_true(self):
        return all([object.is_true() for object in self.expressions])

    def __repr__(self):
        return f"ALL {self.expressions}"

    def as_dict(self):
        dict = {'all': as_dict(self.expressions)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict


class Any():

    def __init__(self, expressions):
        self.expressions = expressions

    def is_true(self):
        return any([object.is_true() for object in self.expressions])

    def __repr__(self):
        return f"ANY {self.expressions}"

    def as_dict(self):
        dict = {'any': as_dict(self.expressions)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict

class Not():

    def __init__(self, expression):
        self.expression = expression

    def is_true(self):
        return not self.expression.is_true()

    def __repr__(self):
        return f"NOT {self.expression}"

    def as_dict(self):
        dict = {'not': as_dict(self.expression)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict


def as_dict(object):
    if hasattr(object, 'as_dict'):
        return object.as_dict()

    if is_list(object):
        return [as_dict(item) for item in object]

    if is_dict(object):
        return {key: as_dict(value) for key, value in object.items()}

    return object
