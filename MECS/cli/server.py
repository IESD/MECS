"""
cli script for registering with the server
Should get user input if no details are specified
"""
import logging
import os

from .. import __version__
from ..config import conf, args, NoOptionError
from ..communication import MECSServer

log = logging.getLogger(__name__)

# on the server we store the data in a folder named for the unit_id
# It's essential these are unique
UNIT_ID = conf.get('MECS', 'unit_id', fallback="unidentified")
REMOTE_FOLDER = f"{UNIT_ID}"

# local folders are specified in the config
ROOT = os.path.expanduser(conf.get('MECS', 'root_folder'))
ARCHIVE_FOLDER = os.path.join(ROOT, conf.get('MECS', 'archive_folder'))
AGGREGATED_FOLDER = os.path.join(ROOT, conf.get('MECS', 'aggregated_folder'))


def get_server(conf):
    try:
        DESTINATION_ROOT = conf.get('MECS-SERVER', 'destination_root')
        USERNAME = conf.get('MECS-SERVER', 'username')
        HOST = conf.get('MECS-SERVER', 'host')
        PORT = conf.get('MECS-SERVER', 'port')
    except NoOptionError as exc:
        log.warning(args.conf)
        log.warning(exc)
        log.warning("required for server upload")
        log.error("No connection to server!")
        exit(0)
    return MECSServer(USERNAME, HOST, PORT, DESTINATION_ROOT)

def register():
    log.debug(f"MECS v{__version__} registering with server")
    server = get_server(conf)
    server.register()

    # ARCHIVE_FOLDER is a local folder to put the data once uploaded
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
    server.create_remote_folder(REMOTE_FOLDER)

def upload():
    log.debug(f"MECS v{__version__} uploading to server")
    UNIT_ID = conf.get('MECS', 'unit_id', fallback="unidentified")
    REMOTE_FOLDER = f"{UNIT_ID}"
    server = get_server(conf)
    server.upload(AGGREGATED_FOLDER, REMOTE_FOLDER, ARCHIVE_FOLDER)
