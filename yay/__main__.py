#!/usr/bin/env python3
import sys
import os

# Core handlers
from yay import core
from yay import http
from yay import files
from yay import script
from yay import input
from yay import xl_cli

# Extension handlers
import yay.arango
import yay.xl_cli

from yay.util import *

def main():

    try:
        # Make sure we can find the file
        filename = get_file(sys.argv[1])

        # Read YAML script
        script = read_yaml_files(filename)

        # Register all files in same directory as handlers
        script_dir = os.path.dirname(os.path.abspath(filename))
        core.register_scripts(script_dir)

        # Initialize variables
        variables = get_variables(script_dir, sys.argv[2:])

        # Process all
        result = core.process_script(script, variables)

    except Exception as exception:
        # import traceback
        # traceback.print_exc()
        print(exception)


def get_file(filename):

    # Add yay extension to filename if not given
    filename = filename if filename.endswith('.yay') else filename + '.yay'

    # Return file if exists
    if os.path.isfile(filename):
        return filename

    # Return file from .yay home
    filename_in_home_folder = os.path.join(os.path.expanduser('~'), '.yay', filename)
    if os.path.isfile(filename_in_home_folder):
        return filename_in_home_folder

    raise YayException(f"Could not find file: {filename}")


def get_variables(script_dir, args):

    variables = {}

    # Load default variables from home dir
    defaultValuesFile = os.path.join(os.path.expanduser('~'), '.yay/default-variables.yaml')
    add_from_yaml_file(defaultValuesFile, variables)

    # Read local context
    context_file = os.path.join(script_dir, 'context.yay')
    if os.path.isfile(context_file):
        selection = get_parameter(args, '-c')
        context = read_yaml_file(context_file)[0]
        if selection in context:
            variables.update(context[selection])
        else:
            print(f"Context {selection} not found in context.yay")
            print_as_yaml(context)

    # Parse arguments into values
    for argument in args:
        if '=' in argument:
            key, value = argument.split('=')
            variables[key] = value

    return variables


def get_parameter(args, parameter):
    use_this_one = False
    for argument in args:
        if use_this_one:
            return argument
        if argument == parameter:
            use_this_one = True

    return 'default'

# Execute script
if __name__ == '__main__':
    main()
