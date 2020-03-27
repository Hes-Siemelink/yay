from yay.util import *


def parse_condition(data):
    if 'object' in data:
        object = get_parameter(data, 'object')

        if 'equals' in data:
            return Equals(object, data['equals'])

        if 'in' in data:
            return Contains(object, data['in'])

        raise YayException("Condition with 'object' should have either 'equals' or 'in'.")

    elif 'all' in data:
        all = get_parameter(data, 'all')
        list = [parse_condition(condition) for condition in all]
        return All(list)

    elif 'any' in data:
        any = get_parameter(data, 'any')
        list = [parse_condition(condition) for condition in any]
        return Any(list)

    else:
        raise YayException("Condition needs 'object', 'all' or 'any'.")


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
        return self.object in self.list

    def __repr__(self):
        return f"{self.object} in {self.list}"

    def as_dict(self):
        dict = {'object': as_dict(self.object), 'in': as_dict(self.list)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict


class All():

    def __init__(self, list):
        self.list = list

    def is_true(self):
        return all([object.is_true() for object in self.list])

    def __repr__(self):
        return f"ALL {self.list}"

    def as_dict(self):
        dict = {'all': as_dict(self.list)}
        if not self.is_true():
            dict['RESULT'] = 'FALSE'
        return dict


class Any():

    def __init__(self, list):
        self.list = list

    def is_true(self):
        return any([object.is_true() for object in self.list])

    def __repr__(self):
        return f"ANY {self.list}"

    def as_dict(self):
        dict = {'any': as_dict(self.list)}
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
