#!/usr/bin/env python3
import sys
import os

# Core handlers
import yay.context
from yay import execution
from yay import core_lib
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
        script_dir = os.path.dirname(os.path.abspath(filename))

        # Read YAML script
        script = read_yaml_files(filename)

        # Read context
        profile = get_command_line_parameter(sys.argv, '-p')
        context = yay.context.get_context(script_dir, profile)

        # Register external commands
        register_scripts(context, script_dir)

        # Initialize variables
        variables = get_variables(sys.argv[2:], context)

        # Process all
        result = execution.run_script(script, variables)

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

def yay_home():
    return os.path.join(os.path.expanduser('~'), '.yay')

def register_scripts(context, script_dir):

    if 'dependencies' in context:
        for package in context['dependencies']:
            version = str(context['dependencies'][package])
            dir = os.path.join(yay_home(), 'packages', package, version)
            yay.context.register_scripts(dir)

    if 'path' in context:
        for dir in context['path']:
            yay.context.register_scripts(dir)

    yay.context.register_scripts(script_dir)


def get_variables(args, context):

    variables = {}

    # Load default variables from home dir
    defaultValuesFile = os.path.join(os.path.expanduser('~'), '.yay/default-variables.yaml')
    add_from_yaml_file(defaultValuesFile, variables)

    # Use local context
    if 'variables' in context:
        variables.update(context['variables'])

    # Parse arguments into values
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
