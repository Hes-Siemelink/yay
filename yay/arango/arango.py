from arango.client import ArangoClient
from yay.execution import command_handler
from yay.util import *

ARANGO_ENDPOINT = 'arango.endpoint'
ARANGO_DATABASE = 'arango.database'

@command_handler('Arango endpoint')
def set_endpoint(data, variables):
    variables[ARANGO_ENDPOINT] = data
    return data

@command_handler('Arango database')
def set_database(data, variables):
    variables[ARANGO_DATABASE] = data
    return data

def get_db(variables):
    endpoint = variables[ARANGO_ENDPOINT]
    database = variables[ARANGO_DATABASE]

    client = ArangoClient(endpoint['protocol'], endpoint['host'], endpoint['port'])

    return client.db(database, endpoint['username'], endpoint['password'])

@command_handler('Arango query')
def run_aql_query(data, variables):
    db = get_db(variables)

    cursor = db.aql.execute(data)

    result = [item for item in cursor]

    return result

@command_handler('Arango insert')
def insert(data, variables):

    collection_name = get_parameter(data, 'in')
    record_data = get_parameter(data, 'record')

    db = get_db(variables)

    collection = db.collection(collection_name)
    collection.insert(record_data)
