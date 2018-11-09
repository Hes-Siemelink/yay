import flask
import threading
import sys

def start():
    thread = threading.Thread(name = 'http.server', target = start_server)
    thread.setDaemon(True)
    thread.start()


def start_server():
    app = flask.Flask("Yay test server")
    app.add_url_rule("/users", view_func = get_users)
    app.env = True
    app.run()


users = [1 ,2, 3]

def get_users():
    return flask.jsonify(users)


if __name__ == '__main__':
    start_server()
