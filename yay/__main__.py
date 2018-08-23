#!/usr/bin/env python3
import sys

# Register handlers
from yay import core
from yay import httprequest

from yay.util import print_as_json
from yay.util import read_yaml_files

def main():

    # Parse arguments
    fileArgument = sys.argv[1]

    variables = {}
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
