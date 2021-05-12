import json
import os.path
import logging

from ..config import config
from .write_output import aggregated_minutely_readings

conf = config()
log = logging.getLogger(__name__)

OUTPUT_FOLDER = os.path.join(os.path.expanduser(conf['MECS']["root_folder"]), conf['MECS']["output_folder"])

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
