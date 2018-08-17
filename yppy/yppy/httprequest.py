#
# HTTP Request task
#
import requests
import json

import config

from yppy.util import get_json_path
from yppy.util import print_as_json

jsonHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}

def process_request(data, variables):
    result = send_request(data, variables)

    if (type(result) is dict):
        variables.update(result)

    return result

def send_request(data, variables):

    if not data: return

    url = config.context['endpoint']
    path = data['path'] if 'path' in data else ''
    body = data['body'] if 'body' in data else None
    method = data['method'] if 'method' in data else 'GET'

    # print("{} {}{}".format(method, url, path))

    if method == 'GET':
        r = requests.get(url + path, headers = jsonHeaders)
    if method == 'POST':
        r = requests.post(url + path, data = json.dumps(body), headers = jsonHeaders)

    if r.status_code != 200:
        print(r.status_code)
        print(r.text)
        return

    result = json.loads(r.text)

    if 'result' in data:
        part = get_json_path(result ,data['result']['path'])

        partResult = {
            data['result']['name']: part
        }
        return partResult
    else:
        return result

# Register task
import core
core.register('request', process_request)
