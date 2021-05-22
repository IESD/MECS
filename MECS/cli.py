import os
from datetime import datetime
import logging
import subprocess
from collections import OrderedDict

from . import __version__
from .config import args, conf, initialise_identifier, initialise_unit_id
# from .communication import upload as uld, register as reg, create_remote_folder
from .communication import MECSServer
from .data_management import generate as gen, aggregate as agg

log = logging.getLogger(__name__)

ROOT = os.path.expanduser(conf.get('MECS', 'root_folder'))
DESTINATION_ROOT = conf.get('MECS', 'destination_root')
HARDWARE_ID = conf.get('MECS', 'HARDWARE_ID', fallback="unidentified")
UNIT_ID = conf.get('MECS', 'unit_id', fallback="unidentified").zfill(5)
OUTPUT_FOLDER = os.path.join(ROOT, conf.get('MECS', 'output_folder'))
AGGREGATED_FOLDER = os.path.join(ROOT, conf.get('MECS', 'aggregated_folder'))
ARCHIVE_FOLDER = os.path.join(ROOT, conf.get('MECS', 'archive_folder'))
USERNAME = conf.get('MECS', 'username')
HOST = conf.get('MECS', 'host')
PORT = conf.get('MECS', 'port')
# we store the data under the hardware id
REMOTE_FOLDER = f"{HARDWARE_ID}/{UNIT_ID}"

server = MECSServer(USERNAME, HOST, PORT, DESTINATION_ROOT)

def status():
    """a simple script to print out the key information"""
    data = OrderedDict({
        "MECS version": __version__,
        "conf": args.conf,
        "HARDWARE_ID": HARDWARE_ID,
        "UNIT_ID": UNIT_ID,
        "DT": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S (UTC)'),
    })
    l1 = max([len(k) for k in data.keys()])
    l2 = max([len(v) for v in data.values()])
    print()
    print("*" * (l1 + l2 + 6))
    for k, v in data.items():
        print(f"* {k:>{l1}}: {v:<{l2}} *")
    print("*" * (l1 + l2 + 6))

def init():
    log.info(f"MECS v{__version__} initialising")
    initialise_identifier(args.conf, conf)
    initialise_unit_id(args.conf, conf)

def generate():
    log.info(f"MECS v{__version__} generating data")
    gen(OUTPUT_FOLDER)

def aggregate():
    log.info(f"MECS v{__version__} aggregating data")
    agg(OUTPUT_FOLDER, AGGREGATED_FOLDER)

def register():
    log.info(f"MECS v{__version__} registering with server")
    os.makedirs(ARCHIVE_FOLDER, exist_ok=True)
    server.register()
    server.create_remote_folder(HARDWARE_ID)
    server.create_remote_folder(REMOTE_FOLDER)

def upload():
    log.info(f"MECS v{__version__} uploading data")
    server.upload(AGGREGATED_FOLDER, REMOTE_FOLDER, ARCHIVE_FOLDER)
