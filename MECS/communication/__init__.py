"""
The communication package allows for:

registering with the server
testing the communication channel
pushing data to the server
"""
import logging
import os.path
import glob
import shutil

# local imports
# conf must be imported first, so logging is configured
from .. import conf, __version__
from .security import register
from .upload import copy_to_server, create_remote_folder

log = logging.getLogger(__name__)

ROOT = os.path.expanduser(conf['MECS']["root_folder"])
OUTPUT_FOLDER = os.path.join(ROOT, conf['MECS']["output_folder"])
AGGREGATED_FOLDER = os.path.join(ROOT, conf['MECS']["aggregated_folder"])
ARCHIVE_FOLDER = os.path.join(ROOT, conf['MECS']["archive_folder"])
DESTINATION_FOLDER = os.path.join(conf['MECS']['destination_folder'], conf['MECS']['data_acquisition_id'])

def initialise():
    """This creates the archive directory and attempts to register with the server specified in the config file."""
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
    register(
        conf['MECS']['port'],
        conf['MECS']['username'],
        conf['MECS']['host']
    )
    create_remote_folder(
        conf['MECS']['data_acquisition_id'],
        conf['MECS']['username'],
        conf['MECS']['host']
    )

def upload():
    """This pushes all the aggregated data up to the server and then archives the data"""
    files = sorted(glob.glob(os.path.join(AGGREGATED_FOLDER, "*.json")))
    for file in files:
        path, fname = os.path.split(file)
        copy_to_server(
            file,
            os.path.join(DESTINATION_FOLDER, fname),
            conf['MECS']['username'],
            conf['MECS']['host']
        )
        shutil.move(file, os.path.join(ARCHIVE_FOLDER, fname))
