from celery import Celery

from yay import vars
from yay import runtime
from yay.execution import YayExecutionContext

app = Celery('yay', backend='rpc://', broker='pyamqp://')
app.conf.update(
    accept_content = ['pickle', 'json', 'msgpack', 'yaml'],
    task_serializer='pickle',
    result_serializer='pickle'
)

def get_celery_app():
    global app
    return app

#
# Execution logic
#

class DistributedYayExecutionContext(YayExecutionContext):

    def run_single_command(self, handler, rawData):

        # Resolve variables
        if handler.delayed_variable_resolver:
            # Execute control structures immediately
            data = rawData
            return handler.handler_method(data, self)
        elif handler.command not in runtime.defaultContext.command_handlers:
            # Execute command handlers locally that are not loaded by default
            data = vars.resolve_variables(rawData, self.variables)
            return handler.handler_method(data, self)
        else:
            # Run remotely through Celery
            data = vars.resolve_variables(rawData, self.variables)
            celery_task = run_command_remotely.apply_async((handler.command, data, self.variables), serializer='pickle')
            (result, self.variables) = celery_task.get(disable_sync_subtasks=False)
            return result


@app.task
def run_command_remotely(command, data, variables):
    context = DistributedYayExecutionContext(variables, runtime.defaultContext.command_handlers)
    result = context.command_handlers[command].handler_method(data, context)

    return result, context.variables