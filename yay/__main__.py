#!/usr/bin/env python3
import sys

from yay.context import YayRuntime, yay_home
from yay.util import *

def main():

    # Get command line arguments
    script_name = sys.argv[1]
    profile = get_command_line_parameter(sys.argv, '-p')
    variables = get_variables(sys.argv[2:])

    # Run script
    try:
        run_yay_script(script_name, profile, variables)
    except Exception as exception:
        import traceback
        traceback.print_exc()
        print(exception)

def run_yay_script(script_name, profile, variables) :

    # Read YAML file
    file = get_file(script_name)
    script = read_yaml_files(file)

    # Initialize runtime
    runtime = YayRuntime()
    script_dir = os.path.dirname(os.path.abspath(file))
    runtime.apply_directory_context(script_dir, profile)
    runtime.update_variables(variables)

    # Run script
    return runtime.run_script(script)


def get_file(filename):

    # Add yay extension to filename if not given
    filename = filename if filename.endswith('.yay') else filename + '.yay'

    # Return file if exists
    if os.path.isfile(filename):
        return filename

    # Return file from .yay home
    filename_in_home_folder = yay_home(filename)
    if os.path.isfile(filename_in_home_folder):
        return filename_in_home_folder

    raise YayException(f"Could not find file: {filename}")


def get_variables(args):

    # Convert arguments into dict
    variables = {}
    for argument in args:
        if '=' in argument:
            key, value = argument.split('=')
            variables[key] = value

    return variables


def get_command_line_parameter(args, parameter, default=''):
    use_this_one = False
    for argument in args:
        if use_this_one:
            return argument
        if argument == parameter:
            use_this_one = True

    return default

# Execute script
if __name__ == '__main__':
    main()
