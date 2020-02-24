import flask
from flask import request

from threading import Thread
from yay.util import *
from yay import execution

global _app
_app = None

def get_app():
    if _app is not None:
        return _app
    else:
        return create_app()

def create_app():
    _app = flask.Flask("Yay server")
    _app.env = 'Webhooks'

    print("Starting Yay server")
    thread = Thread(name = 'http.server', target = _app.run)
    thread.setDaemon(False)
    thread.start()

    return _app

def create_webhook(data, variables):
    app = get_app()
    path = get_parameter(data, 'path')
    app.route(path, methods=['GET'])(handle_request)
    print(f"Started webhook listener on {path}")


def handle_request():
    print("Calling endpoint")

    return "Hello from server!"



# Register command handlers
execution.register('Webhook', create_webhook)


