"""
The communication package allows for:

registering with the server
testing the communication channel
pushing data to the server
"""

# local imports
# conf must be imported first, so logging is configured
from .. import conf, __version__
from .security import register

def initialise():
"""This attempts to register with a server specified in the config file."""
    register(
        conf['MECS']['port'],
        conf['MECS']['username'],
        conf['MECS']['host']
    )
