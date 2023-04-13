import flask
from flask import request

from threading import Thread
from yay.util import *

#
# Server setup
#

app = flask.Flask("Yay test server")
app.env = 'Sample'


#
# Server data and behavior
#

def default_data():
    return {
        '1': 'One',
        '2': 'Two',
        '3': 'Three'
    }

data = default_data()

@app.route('/items', methods=['GET'])
def list_items():
    return flask.jsonify(list(data.keys()))

@app.route('/items', methods=['POST'])
def add_item():
    data = dict(request.json)
    return flask.jsonify(list(data.keys()))

@app.route('/reset', methods=['POST'])
def reset():
    print ("Resetting data")
    data.clear()
    data.update(default_data())
    return ''


def load_demo_data(file_name):
    basePath = os.path.dirname(os.path.realpath(__file__))
    file = os.path.join(basePath, file_name)

    return read_yaml_file(file)[0]

demo_data = load_demo_data('test_server_demo_data.yaml')

@app.route('/recipes', methods=['GET'])
def get_recipe_list():
    recipes = [item['name'] for item in demo_data]

    return flask.jsonify(recipes)

@app.route('/recipe/<name>', methods=['GET'])
def get_recipe(name):
    recipe = next(recipe for recipe in demo_data if recipe['name'] == name)

    return flask.jsonify(recipe)

@app.route('/recipes/search', methods=['GET'])
def search():
    query = request.args.get('keyword')

    recipes = [item['name'] for item in demo_data if query in item['name']]

    return flask.jsonify(recipes)

@app.route('/recipes/options', methods=['GET'])
def get_options():
    vegetarian = request.args.get('vegetarian')
    if vegetarian != None:
        vegetarian = vegetarian=='true'

    recipes = [item['name'] for item in demo_data if vegetarian == None or item['vegetarian'] == vegetarian]

    return flask.jsonify(recipes)

@app.route('/echo/header/<name>', methods=['GET'])
def echo_header(name):
    header = request.headers[name]

    return flask.jsonify({name: header})

@app.route('/echo/cookies', methods=['GET'])
def echo_cookies():
    response = flask.jsonify({'cookies': request.cookies})
    for key, value in request.cookies.items():
        response.set_cookie(key, value)
    return response

#
# Server start
#

def start():
    thread = Thread(name = 'http.server', target = app.run, kwargs={ 'port': 25125 })
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    app.run(port=25125)
