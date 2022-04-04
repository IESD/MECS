"""
MECS configuration handling
"""

import os.path
import logging.config
import argparse
from configparser import ConfigParser

def load_config(path):
    """load configuration from file"""
    if not os.path.exists(path):
        print(f"Error: configuration file {path} not found")
        exit(1)
    config = ConfigParser()
    config.read(path)
    # Configure logging and return
    logging.config.fileConfig(config)
    log = logging.getLogger(__name__)
    log.debug(f"Configuration loaded from {path}")
    return config

def save_config(path, conf):
    """save configuration to file"""
    with open(path, 'w') as f:
        conf.write(f)

# The parser accepts an optional configuration file argument
parser = argparse.ArgumentParser(epilog="For more information see https://github.com/IESD/MECS", description='MECS monitoring system command-line tools')
parser.add_argument('-c', '--conf', default=os.path.expanduser("/home/pi/MECS.ini"), help='configuration file (default ~/.MECS/MECS.ini)')
args = parser.parse_args()
conf = load_config(args.conf)
