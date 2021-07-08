import sys
import os.path
import logging

import pandas as pd

from MECS.plot import plot_as_one

log = logging.getLogger(__name__)

logging.basicConfig(level = logging.DEBUG)

data_path = sys.argv[1]
output_path = sys.argv[2]

os.makedirs(output_path, exist_ok=True)
with os.scandir(data_path) as it:
    for device in it:
        if not device.name.startswith('.'):
            if device.is_file():
                print(f"unexpected file: {device.name}")
                continue
        log.info(f"plotting {device.name}")
        plot_as_one(device.path, os.path.join(output_path, f"{device.name}.png"))
