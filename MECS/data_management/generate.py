"""
This is the high level source of data,
a long-running process
It generates a file on disk every minute
Files are saved into folders generated in the specified location
Each new day is given a new folder
"""

import os.path
import json
import logging

from .minutely import aggregated_minutely_readings, readings

log = logging.getLogger(__name__)

def generate(output_folder, fake):
    """A long-running process, infinitely generating data until it is stopped"""
    log.info(f"Writing {'fake' if fake else 'real'} data files to {output_folder}")
    get_data = readings(fake)
    for data in aggregated_minutely_readings(get_data, delay=1):
        folder = data['dt'].strftime("%Y%m%d")
        os.makedirs(os.path.join(output_folder, folder), exist_ok=True)
        filename = data['dt'].strftime("%Y%m%d%H%M.json")
        data['dt'] = data['dt'].strftime("%Y%m%d%H%M")
        path = os.path.join(output_folder, folder, filename)
        log.debug(f"writing {path}")
        with open(path, "x") as f:
            json.dump(data, f)
