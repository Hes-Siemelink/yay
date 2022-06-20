#
# HTTP commands
#
import requests

from yay.runtime import command_handler
from yay.util import *

jsonHeaders = {'Content-Type': 'application/json', 'Accept': 'application/json'}

HTTP_DEFAULTS = '_http.defaults'


@command_handler('Http endpoint')
def set_http_defaults(data, context):
    if is_scalar(data):
        data = {'url': data}
    context.variables[HTTP_DEFAULTS] = data

    return None


@command_handler('Http GET')
def http_get(data, context):
    if is_scalar(data):
        data = {
            'path': data
        }
    data['method'] = 'GET'
    return process_request(data, context)


@command_handler('Http POST')
def http_post(data, context):
    data['method'] = 'POST'
    return process_request(data, context)


@command_handler('Http PUT')
def http_put(data, context):
    data['method'] = 'PUT'
    return process_request(data, context)


@command_handler('Http DELETE')
def http_delete(data, context):
    data['method'] = 'DELETE'
    return process_request(data, context)


@command_handler('Http')
def process_request(data, context):
    result = send_request(data, context)

    if is_dict(result):
        context.variables.update(result)

    return result


def send_request(data, context):
    if not data: return

    defaults = context.variables.get(HTTP_DEFAULTS)
    if defaults == None:
        defaults = {}

    vars = {**defaults, **data} if defaults else data

    # Parameters
    url = get_parameter(vars, 'url')
    path = vars['path'] if 'path' in vars else ''
    body = json.dumps(vars['body']) if 'body' in vars else None
    method = vars['method'] if 'method' in vars else 'GET'
    file = vars['save as'] if 'save as' in vars else None
    verify = vars['verify certificate'] if 'verify certificate' in vars else True
    cookies = {}
    if 'cookies' in defaults:
        cookies.update(defaults['cookies'])
    if 'cookies' in vars:
        cookies.update(vars['cookies'])

    # Headers
    headers = dict(jsonHeaders)
    if 'headers' in vars:
        headers.update(vars['headers'])

    # Authorization
    auth = get_authorization(vars)

    # Do request
    r = requests.request(method.lower(),
                         url + path,
                         headers=headers,
                         auth=auth,
                         verify=verify,
                         data=body,
                         cookies=cookies)

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


def get_authorization(vars):
    auth = None
    if 'username' in vars and 'password' in vars:
        auth = (vars['username'], vars['password'])

    return auth


def download(data, variables):
    if is_scalar(data):
        data = {
            'path': data
        }
    data['method'] = 'GET'
    return process_request(data, variables)
