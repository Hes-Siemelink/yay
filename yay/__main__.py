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

    variables = {}

    # Load default variables
    defaultValuesFile = os.path.join(os.path.expanduser('~'), '.yay/default-variables.yaml')
    add_from_yaml_file(defaultValuesFile, variables)

    try:
        # Make sure we can find the file
        filename = get_file(sys.argv[1])

        # Parse arguments into values
        for argument in sys.argv[2:]:
            key, value = argument.split('=')
            variables[key] = value

        # Read YAML script
        tasks = read_yaml_files(filename)

        # Process all
        result = core.process_script(tasks, variables)

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


# Execute script
if __name__ == '__main__':
    main()
