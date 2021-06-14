"""
MECS command line interface scripts
"""

import os
from datetime import datetime
import logging
import subprocess
import uuid
from collections import OrderedDict

from . import __version__, update_mecs
from .config import args, conf, initialise_unit_id, NoOptionError, NoSectionError
from .communication import MECSServer
from .mobile_network import connection
from .plot import plot_all
from .data_management.minutely import readings
from .data_management.generate import generate as gen
from .data_management.aggregate import aggregate as agg

log = logging.getLogger(__name__)

# No confirmation that we can communicate with server yet
server = False

# HARDWARE_ID should probably just be calculated every time?
HARDWARE_ID = hex(uuid.getnode())

# UNIT_ID can be unset but is required for upload as it determines the folder
UNIT_ID = conf.get('MECS', 'unit_id', fallback="unidentified").zfill(5)

# we store the data under the hardware id and the unit_id
REMOTE_FOLDER = f"{HARDWARE_ID}/{UNIT_ID}"

# Are we recording fake values?
# TODO: set the default to False so that configuration makes more sense?
FAKE = conf.getboolean('MECS', 'fake_data', fallback=True)


# Are we installing in development mode or as a full install
FULL_INSTALL = conf.getboolean('git', 'install', fallback=False)


# core elements are absolutely necessary for normal operation
# if we don't have these, just report and exit
try:
    GIT_PATH = os.path.expanduser(conf.get('git', 'source_folder'))
    ROOT = os.path.expanduser(conf.get('MECS', 'root_folder'))
    OUTPUT_FOLDER = os.path.join(ROOT, conf.get('MECS', 'output_folder'))
    AGGREGATED_FOLDER = os.path.join(ROOT, conf.get('MECS', 'aggregated_folder'))
    PLOTTING_FOLDER = os.path.join(ROOT, conf.get('MECS', 'plotting_folder', fallback="plots"))
except NoOptionError as exc:
    log.warning(f"Missing option '{exc.option}' in section [{exc.section}] of config file {args.conf}")
    exit(1)
except NoSectionError as exc:
    log.warning(f"Missing section '{exc.section}' in config file {args.conf}")
    exit(1)

# if uploading to a server, these are also required
# Server setup could be placed in a different config section?
try:
    ARCHIVE_FOLDER = os.path.join(ROOT, conf.get('MECS', 'archive_folder'))
    DESTINATION_ROOT = conf.get('MECS-SERVER', 'destination_root')
    USERNAME = conf.get('MECS-SERVER', 'username')
    HOST = conf.get('MECS-SERVER', 'host')
    PORT = conf.get('MECS-SERVER', 'port')
except NoOptionError as exc:
    log.warning(args.conf)
    log.warning(exc)
    log.warning("required for server upload")
else:
    # We can later check the truthyness of this
    server = MECSServer(USERNAME, HOST, PORT, DESTINATION_ROOT)


def pretty_print(dict, heading=True):
    """
    Utility function for printing data to console
    Requires a dict-like containing the data
    Defaults to treating the first element as a heading
    So its best to use an OrderedDict
    """
    l1 = max([len(k) for k in dict.keys()])
    l2 = max([len(str(v)) for v in dict.values()])
    print()
    print("*" * (l1 + l2 + 6))
    for k, v in dict.items():
        print(f"* {k:>{l1}}: {v:<{l2}} *")
        if heading:
            print("*" * (l1 + l2 + 6))
            heading = False
    print("*" * (l1 + l2 + 6))


def status():
    """a simple script to print out some key information"""
    data = OrderedDict({
        "MECS version": __version__,
        "conf": args.conf,
        "HARDWARE_ID": HARDWARE_ID,
        "UNIT_ID": UNIT_ID,
        "DT": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S (UTC)'),
        "FAKE": str(FAKE),
        "Server": f"{USERNAME}@{HOST}:{PORT}" if server else "Not configured"
    })
    pretty_print(data)

def init():
    log.info(f"MECS v{__version__} initialising")
    initialise_unit_id(args.conf, conf)

def generate():
    log.info(f"MECS v{__version__} generating{' fake' if FAKE else ''} data")
    gen(OUTPUT_FOLDER, readings(FAKE))

def aggregate():
    log.info(f"MECS v{__version__} aggregating data")
    agg(OUTPUT_FOLDER, AGGREGATED_FOLDER)

def register():
    if not server:
        log.error("No connection to server!")
        exit(1)
    log.info(f"MECS v{__version__} registering with server")
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
    server.register()
    server.create_remote_folder(HARDWARE_ID)
    server.create_remote_folder(REMOTE_FOLDER)

def upload():
    if not server:
        log.error("No connection to server!")
        exit(1)
    log.info(f"MECS v{__version__} uploading data")
    server.upload(AGGREGATED_FOLDER, REMOTE_FOLDER, ARCHIVE_FOLDER)


def _prepare_output(data):
    """internal function to reorganise data into an ordered dict for printing"""
    output = OrderedDict(data['data'])
    output['dt'] = data['dt'].strftime("%Y-%m-%d %H:%M:%S")
    output.move_to_end('dt', last=False)
    return output


def test():
    data = readings(FAKE)()
    output = _prepare_output(data)
    pretty_print(output)

def test2():
    import time
    readings_func = readings(FAKE)
    try:
        while(True):
            data = readings_func()
            output = _prepare_output(data)
            os.system('clear')
            pretty_print(output)
            time.sleep(2)
    except KeyboardInterrupt:
        pass

def plot():
    plot_all(ARCHIVE_FOLDER, PLOTTING_FOLDER)

def test_connection():
    log.info(f"MECS v{__version__} testing connection")
    with connection(timeout=3600) as conn:
        log.info("working with connection")
    log.info("completed test")

def update():
    update_mecs(GIT_PATH, FULL_INSTALL)
