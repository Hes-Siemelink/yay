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
    data['4'] = 'Four'
    return flask.jsonify({'4': 'Four'})

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
def get_recipes():
    recipes = [item['name'] for item in demo_data]

    return flask.jsonify(recipes)

@app.route('/recipes/search', methods=['GET'])
def get_recipe():
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

#
# Server start
#

def start():
    thread = Thread(name = 'http.server', target = app.run)
    thread.setDaemon(True)
    thread.start()

if __name__ == '__main__':
    app.run()
