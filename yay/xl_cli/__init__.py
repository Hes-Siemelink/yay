from yay import core
from .xl_cli import *

# Register command handlers
core.register('XL apply', xl_apply)