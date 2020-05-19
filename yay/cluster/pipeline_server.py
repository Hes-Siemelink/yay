#
# Http server
#

import flask
from flask import request

from threading import Thread

from yay.util import *
from yay import runtime # FIXME Needed because of cyclic import
from yay.cluster.distributed_execution import DistributedPersistentContext

#
# Server setup
#

flaskapp = flask.Flask("DA Pipeline Server")
flaskapp.env = 'Sample'

#
# API
#

@flaskapp.route('/pipeline', methods=['POST'])
def create_pipeline():
    script = as_list(dict(request.json))

    context = DistributedPersistentContext(command_handlers=runtime.default_command_handlers)
    id = str(context.create_pipeline(script))

    return id

@flaskapp.route('/pipeline/<id>', methods=['GET'])
def get_pipeline(id):

    context = DistributedPersistentContext()
    context.load(id)

    return flask.jsonify(context.script)

@flaskapp.route('/pipeline/<id>/do_one', methods=['POST'])
def do_one(id):

    context = DistributedPersistentContext()
    context.run_next_asynch(id, False)

    return id

@flaskapp.route('/pipeline/<id>/do_all', methods=['POST'])
def do_all(id):

    context = DistributedPersistentContext()
    context.run_next_asynch(id, True)

    return id

#
# Server start
#

def start():
    thread = Thread(name = 'http.server', target = flaskapp.run)
    thread.setDaemon(True)
    thread.start()


if __name__ == '__main__':
    print("\nEndpoints:")
    print("----------")
    for rule in flaskapp.url_map.iter_rules():
        for method in rule.methods:
            if method in ('OPTIONS', 'HEAD'):
                continue
            print(f"{method} {rule}")

    print("\n")

    flaskapp.run()

