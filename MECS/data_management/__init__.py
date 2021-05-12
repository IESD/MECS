"""
Data management

These are the primary functions available for the data management system

generate: This is the high level source of data, a long-running process that generates a file on disk every minute.

aggregate: This is for preparing data for upload, it should be scheduled to run every hour, it merges the available files into one and saves it in a folder ready for uploading.

"""
import glob
import json
import os.path
import logging

import pandas as pd

# conf must be imported first, so logging is configured
from .. import conf, __version__

from .minutely import aggregated_minutely_readings
from .security import register
from .identity import write_identifier

log = logging.getLogger(__name__)

ROOT = os.path.expanduser(conf['MECS']["root_folder"])
OUTPUT_FOLDER = os.path.join(ROOT, conf['MECS']["output_folder"])
AGGREGATED_FOLDER = os.path.join(ROOT, conf['MECS']["aggregated_folder"])

def initialise():
    log.info(f"MECS v{__version__} initialising")
    write_identifier(conf)
    register(
        conf['MECS']['port'],
        conf['MECS']['username'],
        conf['MECS']['host']
    )

def generate():
    try:
        os.makedirs(OUTPUT_FOLDER)
        log.info(f"created folder: {OUTPUT_FOLDER}")
    except FileExistsError:
        pass
    log.info(f"Writing data files to {OUTPUT_FOLDER}")
    for data in aggregated_minutely_readings(delay=1):
        filename = data['dt'].strftime("%Y%m%d%H%M.json")
        data['dt'] = data['dt'].strftime("%Y%m%d%H%M")
        path = os.path.join(OUTPUT_FOLDER, filename)
        log.debug(f"writing {path}")
        with open(path, "x") as f:
            json.dump(data, f)

def aggregate():
    try:
        os.makedirs(AGGREGATED_FOLDER)
        log.info(f"created folder: {AGGREGATED_FOLDER}")
    except FileExistsError:
        pass

    # Grab all the filenames
    files = sorted(glob.glob(os.path.join(OUTPUT_FOLDER, "*.json")))

    if not len(files):
        log.warning(f"No *.json files found in {OUTPUT_FOLDER}")
        return

    # read them into an array
    log.info(f"Aggregating {len(files)} files from {OUTPUT_FOLDER} into {AGGREGATED_FOLDER}")
    result = []
    for filename in files:
        with open(filename, 'r') as f:
            data = json.load(f)
        result.append(data)
        # TODO: move file into temporary folder ready for deletion/archive?

    # convert the array into a pandas dataframe
    df = pd.DataFrame(result)

    # add the datetime index and sort
    df.set_index("dt", inplace=True)
    df.sort_index(inplace=True)

    # Write the aggregated data
    path = os.path.join(AGGREGATED_FOLDER, f"{df.index[0]}-{df.index[-1]}.json")
    log.debug(f"writing {path}")
    try:
        with open(path, "x") as f:
            json.dump(df.to_json(), f)
    except FileExistsError:
        log.warning(f"{path} already exists, ignoring request")
