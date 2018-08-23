#
# HTTP Request task
#
import requests
import json

from yay import core

from yay.util import get_json_path

jsonHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}

def process_request(data, variables):
    result = send_request(data, variables)

    if (type(result) is dict):
        variables.update(result)

    return result

def send_request(data, variables):

    if not data: return

    url = data['url'] if 'url' in data else variables['url']
    path = data['path'] if 'path' in data else ''
    body = data['body'] if 'body' in data else None
    method = data['method'] if 'method' in data else 'GET'

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
core.register('request', process_request)
