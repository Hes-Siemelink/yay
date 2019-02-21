from yay import core
from .arango import *

# Register command handlers
core.register('Arango endpoint', set_endpoint)
core.register('Arango database', set_database)
core.register('Arango query', run_aql_query)
core.register('Arango insert', insert)
