from yay import core
from .xl_cli import *

# Register tasks
core.register('XL apply', xl_apply)