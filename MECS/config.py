"""
MECS configuration handling
"""

import os.path
import logging.config
import argparse
import uuid
from configparser import ConfigParser, NoOptionError, NoSectionError

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

def initialise_unit_id(path, conf):
    """Write a user-specified identifier to the config file"""
    log = logging.getLogger(__name__)
    existing_unit_id = conf.get('MECS', 'unit_id', fallback=False)
    requested_unit_id = input(f"Enter a new Unit ID (currently {existing_unit_id if existing_unit_id else 'not set'}): ")
    confirm = f"Change unit_id from {existing_unit_id}? (y/n) "
    if existing_unit_id and requested_unit_id != existing_unit_id and input(confirm).lower() != "y":
        return
    conf['MECS']['unit_id'] = requested_unit_id
    save_config(path, conf)
    log.info(f"unit_id set: {requested_unit_id}")

# The parser accepts an optional configuration file argument
parser = argparse.ArgumentParser(epilog="For more information see https://github.com/IESD/MECS", description='MECS monitoring system command-line tools')
parser.add_argument('-c', '--conf', default=os.path.expanduser("/home/pi/MECS.ini"), help='configuration file (default ~/.MECS/MECS.ini)')
args = parser.parse_args()
conf = load_config(args.conf)
