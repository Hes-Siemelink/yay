#!/usr/bin/env python3
import sys
import os

# Register handlers
from yay import core
from yay import httprequest
from yay import files

from yay.util import *

def main():

    variables = {}

    # Load default variables
    defaultValuesFile = os.path.join(os.path.expanduser('~'), '.yay/default-variables.yaml')
    add_from_yaml_file(defaultValuesFile, variables)
    print("Default variables:")
    print_as_yaml(variables)


    # Parse arguments
    fileArgument = sys.argv[1]

    for argument in sys.argv[2:]:
        key, value = argument.split('=')
        variables[key] = value

    # Read YAML script
    tasks = read_yaml_files(fileArgument)

    # Process all
    result = core.process_tasks(tasks, variables)
    if result: print_as_json(result)

# Execute script
if __name__ == '__main__':
    main()
