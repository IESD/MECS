"""
MECS command line interface scripts
"""

import os
from datetime import datetime
import logging
import uuid
from collections import OrderedDict

from . import __version__, update_mecs, MECSError
from .config import args, conf, initialise_unit_id, NoOptionError, NoSectionError, save_config
from .communication import MECSServer

log = logging.getLogger(__name__)

# exit codes
WITH_RESTART = 1    # we have set restart = on-failure in the service
WITHOUT_RESTART = 0 # so exit successfully if we don't want to restart

# UNIT_ID can be unset but is required for upload as it determines the folder
UNIT_ID = conf.get('MECS', 'unit_id', fallback="unidentified")

# we store the data under the hardware id and the unit_id
REMOTE_FOLDER = f"{UNIT_ID}"

# Are we recording fake values?
# TODO: set the default to False so that configuration makes more sense?
FAKE = conf.getboolean('data-acquisition', 'fake_data', fallback=False)

# Are we installing in development mode or as a full install
FULL_INSTALL = conf.getboolean('git', 'install', fallback=False)


# core elements are absolutely necessary for normal operation
# if we don't have these, just report and exit
try:
    GIT_PATH = os.path.expanduser(conf.get('git', 'source_folder'))
    GIT_BRANCH = os.path.expanduser(conf.get('git', 'branch'))
    ROOT = os.path.expanduser(conf.get('MECS', 'root_folder'))
    OUTPUT_FOLDER = os.path.join(ROOT, conf.get('MECS', 'output_folder'))
    AGGREGATED_FOLDER = os.path.join(ROOT, conf.get('MECS', 'aggregated_folder'))
    PLOTTING_FOLDER = os.path.join(ROOT, conf.get('MECS', 'plotting_folder', fallback="plots"))
except NoOptionError as exc:
    log.warning(f"Missing option '{exc.option}' in section [{exc.section}] of config file {args.conf}")
    exit(WITHOUT_RESTART)
except NoSectionError as exc:
    log.warning(f"Missing section '{exc.section}' in config file {args.conf}")
    exit(WITHOUT_RESTART)

try:
    # these are required for uploading to a server
    ARCHIVE_FOLDER = os.path.join(ROOT, conf.get('MECS', 'archive_folder'))
    DESTINATION_ROOT = conf.get('MECS-SERVER', 'destination_root')
    USERNAME = conf.get('MECS-SERVER', 'username')
    HOST = conf.get('MECS-SERVER', 'host')
    PORT = conf.get('MECS-SERVER', 'port')
except NoOptionError as exc:
    log.warning(args.conf)
    log.warning(exc)
    log.warning("required for server upload")
    server = False
else:
    # We can later check the truthyness of this
    server = MECSServer(USERNAME, HOST, PORT, DESTINATION_ROOT)

CALIBRATION = os.path.expanduser(conf.get('data-acquisition', 'calibration_file'))
CALIBRATION_SAMPLES = conf.getint('board', 'calibration_samples', fallback=25)

def get_board():
    from .data_acquisition.board import MECSBoard
    calibration_conf = ConfigParser()
    calibration_conf.read(CALIBRATION)
    try:
        return MECSBoard(conf, calibration_conf)
    except MECSError as exc:
        log.warning("Exiting, could not create MECSBoard")
        log.exception(exc)
        exit(WITHOUT_RESTART)
    except Exception as exc:
        log.warning("Unexpected Error!")
        log.exception(exc)
        exit(WITHOUT_RESTART)

def get_readings_function(FAKE):
    if FAKE:
        from .data_management import fake_readings
        log.warning("Generating FAKE data")
        return fake_readings
    board = get_board()
    return board.readings


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
    from .data_management.generate import generate as gen
    gen(OUTPUT_FOLDER, get_readings_function(FAKE))

def aggregate():
    log.info(f"MECS v{__version__} aggregating data")
    from .data_management.aggregate import aggregate as agg
    agg(OUTPUT_FOLDER, AGGREGATED_FOLDER)

def register():
    if not server:
        log.error("No connection to server!")
        exit(WITHOUT_RESTART)
    log.info(f"MECS v{__version__} registering with server")
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
    server.register()
    server.create_remote_folder(REMOTE_FOLDER)

def upload():
    if not server:
        log.error("No connection to server!")
        exit(WITHOUT_RESTART)
    log.info(f"MECS v{__version__} uploading data")
    server.upload(AGGREGATED_FOLDER, REMOTE_FOLDER, ARCHIVE_FOLDER)


def _prepare_output(data):
    """internal function to reorganise data into an ordered dict for printing"""
    output = OrderedDict({k: str(v) for k, v in data['data'].items()})
    output['dt'] = data['dt'].strftime("%Y-%m-%d %H:%M:%S")
    output.move_to_end('dt', last=False)
    return output


def test():
    log.info(f"MECS v{__version__} testing data")
    data = get_readings_function(FAKE)()
    output = _prepare_output(data)
    pretty_print(output)


def test2():
    log.info(f"MECS v{__version__} testing data continuously")
    import time
    readings_func = get_readings_function(FAKE)
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
    from .plot import plot_all
    plot_all(ARCHIVE_FOLDER, PLOTTING_FOLDER)

def plot2():
    from .plot import plot_as_one
    plot_as_one(ARCHIVE_FOLDER, PLOTTING_FOLDER)

def update():
    log.info(f"MECS v{__version__} updating installation")
    update_mecs(GIT_PATH, GIT_BRANCH, full=FULL_INSTALL)

def calibrate():
    log.info(f"MECS v{__version__} calibrating current sensors")

    board = get_board()
    new_conf = board.calibrate(CALIBRATION_SAMPLES)

    for sensor in board.analogue_sensors.values():
        print(sensor)

    confirm = f"Overwrite existing configuration? (y/n) "
    if input(confirm).lower() != "y":
        return

    backup_path = f"{CALIBRATION}.bkp"
    log.info(f"Making backup of config at {backup_path}")
    save_config(backup_path, conf)
    save_config(CALIBRATION, new_conf)
