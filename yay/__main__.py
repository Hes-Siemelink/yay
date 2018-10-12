#!/usr/bin/env python3
import sys
import os

# Register handlers
from yay import core
from yay import httprequest
from yay import files
from yay import script
from yay import input
from yay import xl_cli

from yay.util import *

def main():

    variables = {}

    # Load default variables
    defaultValuesFile = os.path.join(os.path.expanduser('~'), '.yay/default-variables.yaml')
    add_from_yaml_file(defaultValuesFile, variables)

    # Parse arguments
    fileArgument = sys.argv[1]

    for argument in sys.argv[2:]:
        key, value = argument.split('=')
        variables[key] = value

    try:
        # Read YAML script
        tasks = read_yaml_files(fileArgument)

        # Process all
        result = core.process_tasks(tasks, variables)
    except Exception as exception:
        print(exception)

# Execute script
if __name__ == '__main__':
    main()
