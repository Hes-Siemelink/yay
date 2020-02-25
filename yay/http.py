#
# HTTP commands
#
import requests

from yay.context import command_handler
from yay.util import *

jsonHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}

HTTP_DEFAULTS = '_http.defaults'

@command_handler('Http endpoint')
def set_http_defaults(data, variables):

    if is_scalar(data):
        data = {'url': data}
    variables[HTTP_DEFAULTS] = data

    return None

@command_handler('Http GET')
def http_get(data, variables):
    if is_scalar(data):
        data = {
          'path': data
        }
    data['method'] = 'GET'
    return process_request(data, variables)

@command_handler('Http POST')
def http_post(data, variables):
    data['method'] = 'POST'
    return process_request(data, variables)

@command_handler('Http PUT')
def http_put(data, variables):
    data['method'] = 'PUT'
    return process_request(data, variables)

@command_handler('Http DELETE')
def http_delete(data, variables):
    data['method'] = 'DELETE'
    return process_request(data, variables)

@command_handler('Http')
def process_request(data, variables):
    result = send_request(data, variables)

    if is_dict(result):
        variables.update(result)

    return result

def send_request(data, variables):

    if not data: return

    defaults = variables.get(HTTP_DEFAULTS)
    context = {**defaults, **data} if defaults else data

    # Parameters
    url = get_parameter(context, 'url')
    path = context['path'] if 'path' in context else ''
    body = context['body'] if 'body' in context else None
    method = context['method'] if 'method' in context else 'GET'
    file = context['save as'] if 'save as' in context else None

    # Headers
    headers = dict(jsonHeaders)
    if 'headers' in context:
        headers.update(context['headers'])

    # Authorization
    auth = get_authorization(context)

    # Do request
    if method == 'GET':
        r = requests.get(
            url + path,
            headers = headers,
            auth = auth)

    if method == 'POST':
        r = requests.post(
            url + path,
            data = json.dumps(body),
            headers = headers,
            auth = auth)

    if method == 'PUT':
        r = requests.put(
            url + path,
            data = json.dumps(body),
            headers = headers,
            auth = auth)

    if method == 'DELETE':
        r = requests.delete(
            url + path,
            headers = headers,
            auth = auth)

    # Check result
    if r.status_code >= 300:
        print(r.status_code)
        print(r.text)
        return

    if r.status_code > 200:
        return

    # Save to file
    try:
        if file:
            # TODO: stream contents
            with open(file, 'wb') as f:
                f.write(r.content)
            result = {'file': os.path.abspath(file)}
        else:
            result = json.loads(r.text)
    except ValueError:
        result = r.text

    return raw(result)


def get_authorization(context):
    auth = None
    if 'username' in context and 'password' in context:
        auth = (context['username'], context['password'])

    return auth


def download(data, variables):
    if is_scalar(data):
        data = {
            'path': data
        }
    data['method'] = 'GET'
    return process_request(data, variables)
