"""
MECS is a system for monitoring sensors attached to a raspberry pi
It includes packages for:
    data acquisition from the sensors
    managing data locally
    uploading data to a server
"""

import pkg_resources

__version__ = pkg_resources.get_distribution('MECS').version
