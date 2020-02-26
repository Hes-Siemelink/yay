from arango.client import ArangoClient
from yay.context import command_handler
from yay.util import *

ARANGO_ENDPOINT = 'arango.endpoint'
ARANGO_DATABASE = 'arango.database'

@command_handler('Arango endpoint')
def set_endpoint(data, context):
    context.variables[ARANGO_ENDPOINT] = data
    return data

@command_handler('Arango database')
def set_database(data, context):
    context.variables[ARANGO_DATABASE] = data
    return data

def get_db(context):
    endpoint = context.variables[ARANGO_ENDPOINT]
    database = context.variables[ARANGO_DATABASE]

    client = ArangoClient(endpoint['protocol'], endpoint['host'], endpoint['port'])

    return client.db(database, endpoint['username'], endpoint['password'])

@command_handler('Arango query')
def run_aql_query(data, context):
    db = get_db(context)

    cursor = db.aql.execute(data)

    result = [item for item in cursor]

    return result

@command_handler('Arango insert')
def insert(data, context):

    collection_name = get_parameter(data, 'in')
    record_data = get_parameter(data, 'record')

    db = get_db(context)

    collection = db.collection(collection_name)
    collection.insert(record_data)
