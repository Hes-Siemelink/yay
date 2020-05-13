from time import sleep

from celery import Celery
import pymongo
from bson.objectid import ObjectId

from yay import vars
from yay import runtime
from yay.util import *
from yay.execution import YayExecutionContext
from yay.cluster.persistent_execution import PersistentExecutionContext

app = Celery('yay', backend='rpc://', broker='pyamqp://')
app.conf.update(
    accept_content=['pickle', 'json', 'msgpack', 'yaml'],
    task_serializer='pickle',
    result_serializer='pickle'
)


def get_celery_app():
    global app
    return app


#
# Execution logic
#

class DistributedContext(YayExecutionContext):

    def run_single_command(self, handler, rawData):

        # Execute control structures immediately
        if handler.delayed_variable_resolver:
            data = rawData
            return handler.handler_method(data, self)

        # Execute command handlers locally that are not loaded by default
        elif handler.command not in runtime.default_command_handlers:
            data = vars.resolve_variables(rawData, self.variables)
            return handler.handler_method(data, self)

        # Run remotely through Celery
        else:
            data = vars.resolve_variables(rawData, self.variables)
            celery_task = run_command_remotely.apply_async((handler.command, data, self.variables), serializer='pickle')
            (result, self.variables) = celery_task.get(disable_sync_subtasks=False)
            return result


@app.task
def run_command_remotely(command, data, variables):
    context = DistributedContext(variables, runtime.default_command_handlers)
    result = context.command_handlers[command].handler_method(data, context)

    return result, context.variables


mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
yay_db = mongo_client["yay-db"]

script_collection = yay_db["scripts"]


class DistributedPersistentContext(PersistentExecutionContext):

    def run_from_database(self, id):
        celery_task = do_next_step.apply_async((id, ), serializer='pickle')

        finished = False
        while not finished:
            sleep(1)

            self.load(id)

            finished = self.script['status'] not in ['Planned', 'In progress']

        self.raise_error(self.script)

    def run_next_asynch(self, id):
        do_next_step.apply_async((id, ), serializer='pickle')

@app.task
def do_next_step(id):
    context = DistributedPersistentContext(command_handlers=runtime.default_command_handlers)
    context.load(id)

    try:
        context.run_next_step(context.script)
    except Exception as e:
        context.script['status'] = 'Failed'
        context.script['error'] = str(e)
        context.update()

    if context.script['status'] not in ['Completed', 'Failed']:
        context.run_next_asynch(id)
