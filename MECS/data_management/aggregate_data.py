import glob
import os.path
import json

import pandas as pd

OUTPUT_FOLDER = "../../output"

# Grab all the filenames
files = sorted(glob.glob(os.path.join(OUTPUT_FOLDER, "*.json")))

# read them into an array
result = []
for filename in files:
    with open(filename, 'r') as f:
        data = json.load(f)
    result.append(data)

# convert the array into a dataframe
# add the datetime index and sort
df = pd.DataFrame(result)
# df['dt'] = pd.to_datetime(df['dt'])
df.set_index("dt", inplace=True)
df.sort_index(inplace=True)


print(df.to_json())
# Write the aggregated data

# write_file = f"{df.index[0]}-{df.index[-1]}.json"
#
# with open(write_file, "w") as f:
#     json.dump(df.to_json(), f)
