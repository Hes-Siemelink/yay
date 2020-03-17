import flask

from threading import Thread
from yay.context import command_handler
from yay.util import *

app = flask.Flask("Yay webhook handler")
app.env = 'Webhooks'

global webhook_server_started
webhook_server_started = False

@command_handler('Webhook', delayed_variable_resolver=True)
def add_webhook(data, context):
    path = get_parameter(data, 'path')
    actions = get_parameter(data, 'Do')
    app.add_url_rule(
        path,
        path,
        lambda: context.run_task({'Do': actions})
    )

    print(str(app.view_functions))
    global webhook_server_started
    if not webhook_server_started:
        start()
        webhook_server_started = True

#
# Server start
#


def start():
    thread = Thread(name = 'http.server', target = app.run)
    thread.setDaemon(False)
    thread.start()

