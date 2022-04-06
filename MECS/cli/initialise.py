"""
This script could do a lot more
Perhaps check all necessary parameters and offer to fill them or update them
e.g. server details
this should be integrated with the default config files and make_mecs
"""
import logging

from .. import __version__

from ..config import args, conf, save_config

log = logging.getLogger(__name__)


def initialise():
    log.debug(f"MECS v{__version__} initialising")
    initialise_unit_id(args.conf, conf)
    initialise_type(args.conf, conf)
    initialise_host(args.conf, conf)
    initialise_username(args.conf, conf)

def initialise_unit_id(path, conf):
    """Write a user-specified identifier to the config file"""
    existing_unit_id = conf.get('MECS', 'unit_id', fallback=False)
    requested_unit_id = input(f"Enter a new Unit ID (currently {existing_unit_id if existing_unit_id else 'not set'}): ")
    confirm = f"Change unit_id from {existing_unit_id}? (y/n) "
    if existing_unit_id and requested_unit_id != existing_unit_id and input(confirm).lower() != "y":
        return
    conf['MECS']['unit_id'] = requested_unit_id
    save_config(path, conf)
    log.info(f"unit_id set: {requested_unit_id}")

def initialise_type(path, conf):
    """Write AC or DC to the config file"""
    existing_type = conf.get('MECS', 'unit_type', fallback=False)
    requested_type = input(f"Unit type (AC or DC, currently {existing_type if existing_type else 'not set'}): ").upper()
    if requested_type not in ["AC", "DC"]:
        print(f"Invalid type [{requested_type}] (should be AC or DC")
        return
    confirm = f"Change type from {existing_type} to {requested_type}? (y/n) "
    if existing_type and requested_type != existing_type and input(confirm).lower() != "y":
        return
    conf['MECS']['unit_type'] = requested_type
    device_filename = f'{requested_type.lower()}_devices.json'
    conf['MECS']['devices_config_path'] = f'/home/pi/{device_filename}'
    save_config(path, conf)
    log.info(f"unit_type set: {requested_type}")
    log.info(f"using {requested_type} config file: {device_filename}")

def initialise_host(path, conf):
    """Setup server host"""
    existing_host = conf.get('MECS-SERVER', 'host', fallback=False)
    requested_host = input(f"Host (currently {existing_host or 'not set'}): ")
    confirm = f"Change host from {existing_host} to {requested_host}? (y/n) "
    if existing_host and requested_host != existing_host and input(confirm).lower() != "y":
        return
    conf['MECS-SERVER']['host'] = requested_host
    save_config(path, conf)
    log.info(f"host set: {requested_host}")

def initialise_username(path, conf):
    """Setup server username"""
    existing_username = conf.get('MECS-SERVER', 'username', fallback=False)
    requested_username = input(f"Username (currently {existing_username or 'not set'}): ")
    confirm = f"Change username from {existing_username} to {requested_username}? (y/n) "
    if existing_username and requested_username != existing_username and input(confirm).lower() != "y":
        return
    conf['MECS-SERVER']['username'] = requested_username
    save_config(path, conf)
    log.info(f"username set: {requested_username}")
