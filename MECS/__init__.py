import sys
import os
import os.path
import logging
import logging.config
from configparser import ConfigParser

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
