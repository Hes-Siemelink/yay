import copy
import os

from yay import YayException
from yay.execution import process_script
from yay.vars import OUTPUT_VARIABLE
from yay.util import read_yaml_file, get_parameter


#
# Yay-context.yaml
#

def get_context(script_dir, profile_name):
    context_file = os.path.join(script_dir, 'yay-context.yaml')
    if not os.path.isfile(context_file):
        return {}

    context = read_yaml_file(context_file)[0]
    apply_profile(context, profile_name)

    return context


def apply_profile(context, profile_name):
    profiles = context.pop('profiles', None)
    if profile_name:
        if profiles and profile_name in profiles:
            dict_merge(context, profiles[profile_name])
        else:
            raise YayException(f"Profile '{profile_name}' not found in yay-context.yaml")


def dict_merge(context, profile):
    for key in profile:
        if key in context:
            context[key].update(profile[key])
        else:
            context[key] = profile[key]

#
# Command handlers
#

handlers = {}


class Handler():

    def __init__(self, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.handler_method = handler_method
        self.delayed_variable_resolver = delayed_variable_resolver
        self.list_processor = list_processor


def register(command, handler_method, delayed_variable_resolver=False, list_processor=False):
    handlers[command] = Handler(handler_method, delayed_variable_resolver, list_processor)


def command_handler(command, delayed_variable_resolver=False, list_processor=False):
    def inner_decorator(handler_function):
        register(command, handler_function, delayed_variable_resolver=delayed_variable_resolver, list_processor=list_processor)
        return handler_function
    return inner_decorator


def register_scripts(path):

    # Resolve ~ for home dir
    path = os.path.expanduser(path)

    # Create a custom handler for each script in the directory by
    # routing it to 'exectute_yay_file' using a lambda function.
    for filename in os.listdir(path):
        if filename.endswith('.yay'):
            handler_name = to_handler_name(filename)
            filename = os.path.join(path, filename)
            register(handler_name,
                     lambda data, variables, file = filename:
                     execute_yay_file(data, variables, file))


def to_handler_name(filename):
    filename = filename.replace('.yay', '')
    filename = filename.replace('-', ' ')
    return filename


def execute_yay_file(data, variables, file = None):
    if file == None:
        file = get_parameter(data, 'file')

    # Read YAML script
    script = read_yaml_file(file)

    # Process all
    vars = copy.deepcopy(variables)
    if file in data:
        del data['file']

    # FIXME handle case if data is str or list
    vars.update(data)

    process_script(script, vars)

    return vars.get(OUTPUT_VARIABLE)