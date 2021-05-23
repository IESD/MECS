"""
This is for preparing data for upload,
it should be scheduled to run every hour,
it merges the available files into one file per day
and saves it in a folder ready for uploading.
"""
import glob
import json
import os.path
import logging

import pandas as pd

log = logging.getLogger(__name__)

def aggregate(source_folder, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    folders = sorted(glob.glob(os.path.join(source_folder, "*")))
    for folder in folders:
        df = aggregate_folder(folder)
        day = df.index[0].strftime("%Y%m%d")
        path = os.path.join(destination_folder, f"{day}.json")
        log.info(f"writing to {path}")
        df.to_json(path, orient="split", date_format="iso")

def aggregate_folder(folder):
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
    df['dt'] = pd.to_datetime(df['dt'])
    df.set_index("dt", inplace=True)
    df.sort_index(inplace=True)

    return df
