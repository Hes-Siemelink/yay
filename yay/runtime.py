import copy
import importlib

from yay.util import *
from yay.execution import YayExecutionContext, CommandHandler
from yay.vars import OUTPUT_VARIABLE

#
# Register command handlers
#

default_command_handlers = {}

def command_handler(command, delayed_variable_resolver=False, list_processor=False):
    def inner_decorator(handler_function):
        global default_command_handlers
        default_command_handlers[command] = CommandHandler(command, handler_function, delayed_variable_resolver, list_processor)
        return handler_function

    return inner_decorator

#
# Import standard handlers
#

importlib.import_module('yay.core_lib')
importlib.import_module('yay.http_handlers')
importlib.import_module('yay.files')
importlib.import_module('yay.script')
importlib.import_module('yay.input')
importlib.import_module('yay.xl_cli')
importlib.import_module('yay.arango')
importlib.import_module('yay.webhook')


@command_handler('Execute yay file')
def run_yay_file(data, context, file=None):
    if file == None:
        file = get_parameter(data, 'file')

    # Read YAML script
    script = read_yaml_file(file)

    # Run script
    scriptContext = copy.deepcopy(context)
    scriptContext.variables.update(data)
    scriptContext.run_script(script)

    return scriptContext.output()

#
# Default context
#

# Use distributed context
# from yay.cluster.distributed_execution import DistributedContext, DistributedPersistentContext, get_celery_app
# app = get_celery_app()
# defaultContext = DistributedPersistentContext(command_handlers=default_command_handlers)

# Use persistent context
# from yay.cluster.persistent_execution import PersistentExecutionContext
# defaultContext = PersistentExecutionContext(command_handlers=default_command_handlers)

# Use normal context
defaultContext = YayExecutionContext(command_handlers=default_command_handlers)


#
# Create runtime
#

class YayRuntime():

    def __init__(self, context=defaultContext):
        self.context = copy.deepcopy(context)

    def add_command_handler(self, command, handler_method, delayed_variable_resolver=False, list_processor=False):
        self.context.add_command_handler(command, handler_method, delayed_variable_resolver, list_processor)

    def update_variables(self, variables):
        self.context.variables.update(variables)
        self.context.variables[OUTPUT_VARIABLE] = ''

    def run_script(self, script):
        return self.context.run_script(script)

    def run_task(self, data):
        return self.context.run_task(data)

    def apply_directory_context(self, script_dir, profile):
        context_file = os.path.join(script_dir, 'yay-context.yaml')
        context = read_yaml_file(context_file)[0] if os.path.isfile(context_file) else {}

        self.apply_profile(context, profile)
        self.register_scripts_from_context(context)
        self.register_scripts_in_directory(script_dir)
        self.load_variables(context)

        return context

    def apply_profile(self, context, profile_name):
        profiles = context.pop('profiles', None)
        if profile_name:
            if profiles and profile_name in profiles:
                dict_merge(context, profiles[profile_name])
            else:
                raise YayException(f"Profile '{profile_name}' not found in yay-context.yaml")

    def register_scripts_from_context(self, context):

        if 'dependencies' in context:
            for package in context['dependencies']:
                version = str(context['dependencies'][package])
                dir = yay_home('packages', package, version)
                self.register_scripts_in_directory(dir)

        if 'path' in context:
            for dir in context['path']:
                self.register_scripts_in_directory(dir)

    def load_variables(self, context):

        # Load default variables from home dir
        defaultValuesFile = yay_home('default-variables.yaml')
        add_from_yaml_file(defaultValuesFile, self.context.variables)

        # Use local context
        if 'variables' in context:
            self.context.variables.update(context['variables'])

    def register_scripts_in_directory(self, path):

        # Resolve ~ for home dir
        path = os.path.expanduser(path)

        # Create a custom handler for each script in the directory by
        # routing it to 'exectute_yay_file' using a lambda function.
        for filename in os.listdir(path):
            if filename.endswith('.yay'):
                handler_name = to_handler_name(filename)
                filename = os.path.join(path, filename)
                self.context.add_command_handler(handler_name,
                                                 lambda data, variables, file=filename: run_yay_file(data, variables, file))


def yay_home(*paths):
    home = os.path.join(os.path.expanduser('~'), '.yay')
    return os.path.join(home, *paths)


def to_handler_name(filename):
    filename = filename.replace('.yay', '')
    filename = filename.replace('-', ' ')
    return filename
