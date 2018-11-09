import flask
from flask import request

from threading import Thread

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


search_data = {
    'My stuff': ['apples, pears'],
    'Other stuff': ['oranges', 'lemons']
}

@app.route('/rest/search', methods=['GET'])
def search():
    query = request.args.get('query')

    search_result = {}
    if query:
        for key in search_data:
            if query in key:
                search_result[key] = search_data[key]
    else:
        search_result = search_data

    return flask.jsonify(search_result)


#
# Server start
#

def start():
    thread = Thread(name = 'http.server', target = app.run)
    thread.setDaemon(True)
    thread.start()

if __name__ == '__main__':
    app.run()
