"""
grab data and write it to files

here we generate one file per minute
Obviously we want to minimise the data kept in memory
And writing to disk regularly minimises potential data loss
There is a balance, we might be happy to gather an hour of data before writing to a file.
"""

import json
import os.path
from time import sleep
from collections import defaultdict

import pandas as pd

from get_input import raw_readings

OUTPUT_FOLDER = "../../output"

def aggregated_minutely_readings():
    data = []
    last_minute = raw_readings()['dt'].replace(second=0, microsecond=0)
    while True:
        readings = raw_readings()
        if last_minute != readings['dt'].replace(second=0, microsecond=0):
            result = pd.DataFrame(data).mean().to_dict()
            result['dt'] = last_minute
            yield result
            data = []
            last_minute = readings['dt'].replace(second=0, microsecond=0)
        data.append(readings['data'])
        sleep(1)


for data in aggregated_minutely_readings():
    filename = data['dt'].strftime("%Y%m%d%H%M.json")
    data['dt'] = data['dt'].strftime("%Y%m%d%H%M")
    path = os.path.join(OUTPUT_FOLDER, filename)
    with open(path, "w") as f:
        json.dump(data, f)
