"""
MECS is a system for monitoring sensors attached to a raspberry pi
It includes packages for:
    data acquisition from the sensors
    regularly writing data to disk
    aggregating data into summary files
    uploading data to a server
"""

import pkg_resources

__version__ = pkg_resources.get_distribution('MECS').version
