#
# HTTP Request task
#
import requests
import json

from yay import core

from yay.util import *

jsonHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}

def http_get(data, variables):
    data['method'] = 'GET'
    return process_request(data, variables)

def http_post(data, variables):
    data['method'] = 'POST'
    return process_request(data, variables)

def http_put(data, variables):
    data['method'] = 'PUT'
    return process_request(data, variables)

def http_delete(data, variables):
    data['method'] = 'DELETE'
    return process_request(data, variables)

def process_request(data, variables):
    result = send_request(data, variables)

    if is_dict(result):
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
    if method == 'PUT':
        r = requests.put(url + path, data = json.dumps(body), headers = jsonHeaders)
    if method == 'DELETE':
        r = requests.delete(url + path, headers = jsonHeaders)

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

# Register tasks
core.register('http.get', http_get)
core.register('http.post', http_post)
core.register('http.put', http_put)
core.register('http.delete', http_delete)
core.register('http.request', process_request)
