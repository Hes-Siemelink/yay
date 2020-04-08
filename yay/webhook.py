import flask
from flask import request

from copy import deepcopy
from threading import Thread

from yay.runtime import command_handler
from yay.util import *

app = flask.Flask("Yay webhook handler")
app.testing = False


@command_handler('On Http request', delayed_variable_resolver=True)
def add_webhook(data, context):
    handler_context = deepcopy(context)
    for path in data:
        for method in data[path]:
            actions = get_parameter(data[path], method)
            path = make_flask_path(path)
            add_rule(path, handler_context, actions, methods=[method])

    start_server()


def add_rule(path, context, actions, **options):
    app.add_url_rule(
        path,
        path,
        lambda **parameters: run_rule(context, actions, parameters),
        **options
    )


def run_rule(context, actions, parameters):
    my_context = deepcopy(context)
    print(str(request.json))
    if request.json:
        my_context.variables['body'] = request.json
    my_context.variables['headers'] = dict(request.headers)
    my_context.variables.update(parameters)

    output = my_context.run_task({'Do': actions})

    return flask.jsonify(output)


def make_flask_path(swagger_path):
    return swagger_path.replace('{', '<').replace('}', '>')


global webhook_server_started
webhook_server_started = False


def start_server():
    global webhook_server_started
    if not webhook_server_started:
        thread = Thread(name='http.server', target=app.run)
        thread.setDaemon(False)
        thread.start()
        webhook_server_started = True
