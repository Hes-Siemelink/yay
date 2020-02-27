#!/usr/bin/env python3
import sys

from yay.context import YayContext, yay_home
from yay.util import *

def main():

    try:
        # Make sure we can find the file
        filename = get_file(sys.argv[1])
        script_dir = os.path.dirname(os.path.abspath(filename))

        # Read YAML script
        script = read_yaml_files(filename)

        # Load context
        profile = get_command_line_parameter(sys.argv, '-p')

        context = YayContext()
        context.apply_directory_context(script_dir, profile)

        # Initialize variables
        commandLineVars = get_variables(sys.argv[2:])
        context.runner.variables.update(commandLineVars)

        # Process all
        result = context.run_script(script)

    except Exception as exception:
        import traceback
        traceback.print_exc()
        print(exception)


def get_file(filename):

    # Add yay extension to filename if not given
    filename = filename if filename.endswith('.yay') else filename + '.yay'

    # Return file if exists
    if os.path.isfile(filename):
        return filename

    # Return file from .yay home
    filename_in_home_folder = os.path.join(yay_home(), filename)
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
