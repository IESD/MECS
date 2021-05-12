"""
Load configuration settings from file and make them available to the project
"""

import sys
import os.path
import logging.config
from configparser import ConfigParser
import pkg_resources

__version__ = pkg_resources.get_distribution('MECS').version

def config_file():
    """determine path for file - default or user provided"""
    try:
        return os.path.expanduser(sys.argv[1])
    except IndexError:
        return os.path.expanduser("~/.MECS/MECS.ini")

def config():
    """load configuration from file"""
    path = config_file()

    if not os.path.exists(path):
        print(f"Error: configuration file {path} not found")
        exit(1)

    config = ConfigParser()
    config.read(path)

    # Configure logging and return
    logging.config.fileConfig(config)
    return config

conf = config()
