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
