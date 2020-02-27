import copy

from yay import vars
from yay import execution
from yay.util import *

#
# Yay-context.yaml
#

class YayContext:

    def __init__(self, context = None):
        self.variables = {}
        self.command_handlers = {}

        if context:
            self.variables = copy.deepcopy(context.variables)
            self.command_handlers = copy.deepcopy(context.command_handlers)


    def apply_directory_context(self, script_dir, profile):
        context_file = os.path.join(script_dir, 'yay-context.yaml')
        if not os.path.isfile(context_file):
            return {}

        context = read_yaml_file(context_file)[0]
        self.apply_profile(context, profile)

        self.register_scripts_from_context(context)
        self.register_scripts(script_dir)

        self.load_variables(context)

        return context


    def apply_profile(self, context, profile_name):
        profiles = context.pop('profiles', None)
        if profile_name:
            if profiles and profile_name in profiles:
                self.dict_merge(context, profiles[profile_name])
            else:
                raise YayException(f"Profile '{profile_name}' not found in yay-context.yaml")


    def dict_merge(self, context, profile):
        for key in profile:
            if key in context:
                context[key].update(profile[key])
            else:
                context[key] = profile[key]

    def register_scripts_from_context(self, context):

        if 'dependencies' in context:
            for package in context['dependencies']:
                version = str(context['dependencies'][package])
                dir = os.path.join(yay_home(), 'packages', package, version)
                self.register_scripts(dir)

        if 'path' in context:
            for dir in context['path']:
                self.register_scripts(dir)

    def load_variables(self, context):

        # Load default variables from home dir
        defaultValuesFile = os.path.join(yay_home(), 'default-variables.yaml')
        add_from_yaml_file(defaultValuesFile, self.variables)

        # Use local context
        if 'variables' in context:
            self.variables.update(context['variables'])

    def run_script(self, script):
        return execution.run_script(script, self)

    def run_task(self, data):
        return execution.run_task(data, self)

    def add_command_handler(self, command, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.command_handlers[command] = CommandHandler(handler_method, delayed_variable_resolver, list_processor)

    def register_scripts(self, path):

        # Resolve ~ for home dir
        path = os.path.expanduser(path)

        # Create a custom handler for each script in the directory by
        # routing it to 'exectute_yay_file' using a lambda function.
        for filename in os.listdir(path):
            if filename.endswith('.yay'):
                handler_name = to_handler_name(filename)
                filename = os.path.join(path, filename)
                self.add_command_handler(handler_name,
                                            lambda data, variables, file = filename: run_yay_file(data, variables, file))

def yay_home():
    return os.path.join(os.path.expanduser('~'), '.yay')

#
# Command handlers
#

defaultContext = YayContext()

class CommandHandler():
    def __init__(self, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.handler_method = handler_method
        self.delayed_variable_resolver = delayed_variable_resolver
        self.list_processor = list_processor

def command_handler(command, delayed_variable_resolver=False, list_processor=False):
    def inner_decorator(handler_function):
        defaultContext.add_command_handler(command, handler_function, delayed_variable_resolver=delayed_variable_resolver, list_processor=list_processor)
        return handler_function
    return inner_decorator


def to_handler_name(filename):
    filename = filename.replace('.yay', '')
    filename = filename.replace('-', ' ')
    return filename

@command_handler('Execute yay file')
def run_yay_file(data, context, file = None):
    if file == None:
        file = get_parameter(data, 'file')

    # Read YAML script
    script = read_yaml_file(file)

    scriptContext = YayContext(context)
    scriptContext.variables.update(data)
    scriptContext.run_script(script)

    return scriptContext.variables.get(vars.OUTPUT_VARIABLE)

#
# Import standard libraries and register command handlers in default context
#

import importlib
importlib.import_module('yay.core_lib')
importlib.import_module('yay.http')
importlib.import_module('yay.files')
importlib.import_module('yay.script')
importlib.import_module('yay.input')
importlib.import_module('yay.xl_cli')
importlib.import_module('yay.arango')
