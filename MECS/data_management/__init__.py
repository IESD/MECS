"""
Data management

These are the primary functions available for the data management system:

generate: This is the high level source of data, a long-running process that generates a file on disk every minute.
aggregate: This is for preparing data for upload, it should be scheduled to run every hour, it merges the available files into one and saves it in a folder ready for uploading.

"""
import glob
import json
import os.path
import logging

import pandas as pd

# conf must be imported first, so logging is configured
from .minutely import aggregated_minutely_readings


log = logging.getLogger(__name__)

def generate(output_folder, fake):
    """This one is long-running, infinitely generating data until it is stopped"""
    log.info(f"Writing {'fake' if fake else 'real'} data files to {output_folder}")
    for data in aggregated_minutely_readings(fake, delay=1):
        folder = data['dt'].strftime("%Y%m%d")
        os.makedirs(os.path.join(output_folder, folder), exist_ok=True)
        filename = data['dt'].strftime("%Y%m%d%H%M.json")
        data['dt'] = data['dt'].strftime("%Y%m%d%H%M")
        path = os.path.join(output_folder, folder, filename)
        log.debug(f"writing {path}")
        with open(path, "x") as f:
            json.dump(data, f)


def aggregate(source_folder, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    # Grab all the folders
    folders = sorted(glob.glob(os.path.join(source_folder, "*")))
    for folder in folders:
        df = aggregate_folder(folder)
        # path = os.path.join(destination_folder, f"{df.index[0]}-{df.index[-1]}.json")
        day = df.index[0][:8]
        path = os.path.join(destination_folder, f"{day}.json")
        try:
            with open(path, "w") as f:
                log.info(f"writing to {path}")
                json.dump(df.to_json(), f)
        except FileExistsError:
            log.warning(f"{path} already exists, ignoring request")


def aggregate_folder(folder):
    # Grab all the filenames
    files = sorted(glob.glob(os.path.join(folder, "*.json")))
    if not len(files):
        log.warning(f"No *.json files found in {folder}")
        return
    log.debug(f"{len(files)} *.json files found in {folder}")

    # read them into an array
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

    return df
