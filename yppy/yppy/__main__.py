#!/usr/bin/env python3
import sys

import core
import config
import httprequest
import vars

from yppy.util import print_as_json
from yppy.util import print_as_yaml
from yppy.util import read_yaml_files

def main():

    # Parse arguments
    endpoint = sys.argv[1]
    fileArgument = sys.argv[2]

    config.context['endpoint'] = endpoint

    # Read YAML script
    tasks = read_yaml_files(fileArgument)

    # Process all
    result = core.process_tasks(tasks)
    if result: print_as_json(result)

# Execute script
main()
