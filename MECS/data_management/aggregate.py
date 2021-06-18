"""
This is for preparing data for upload,
it should be scheduled to run every hour,
it merges the available files into one file per day
and saves it in a folder ready for uploading.
"""
from datetime import date
import glob
import json
import os.path
import shutil
import tarfile
import logging

import pandas as pd

log = logging.getLogger(__name__)

def make_archive_file(output_filename, source_dir):
    """converts a folder full of minutely json files into a single, compressed archive file"""
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def aggregate(source_folder, destination_folder):
    """
    Converts minutely files for a day into a single file
    Creates an aggregated file in the destination directory for each folder in the source directory
    """
    today = date.today().strftime("%Y%m%d")
    os.makedirs(destination_folder, exist_ok=True)
    folders = sorted(next(os.walk(source_folder))[1])
    for folder in folders:
        source_path = os.path.join(source_folder, folder)
        aggregated_path = os.path.join(destination_folder, f"{folder}.json")
        df = aggregate_folder(source_path)
        log.info(f"writing to {aggregated_path}")
        df.to_json(aggregated_path, orient="split", date_format="iso")

        # archiving when the data is from before today
        if(folder < today):
            archive_path = os.path.join(source_folder, f"{folder}.tar.gz")
            log.info(f"archiving {source_path} to {archive_path}")
            make_archive_file(archive_path, source_path)
            log.info(f"deleting original {source_path}")
            shutil.rmtree(source_path)


def aggregate_folder(folder):
    """This does the aggregation job, merging the files into one dataframe"""
    files = sorted(glob.glob(os.path.join(folder, "*.json")))
    if not len(files):
        log.warning(f"No *.json files found in {folder}")
        return
    log.debug(f"{len(files)} *.json files found in {folder}")

    # read them into an array
    result = []
    for filename in files:
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
        except json.decoder.JSONDecodeError as exc:
            log.warning(exc)
            log.warning(f"skipping {filename}")
            continue
        result.append(data)
        # TODO: move file into temporary folder ready for deletion/archive?

    # convert the array into a pandas dataframe
    df = pd.DataFrame(result)

    # add the datetime index and sort
    df['dt'] = pd.to_datetime(df['dt'])
    df.set_index("dt", inplace=True)
    df.sort_index(inplace=True)

    return df
