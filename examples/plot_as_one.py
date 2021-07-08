import sys
from MECS.plot import plot_as_one

data_path = sys.argv[1]
output_file = sys.argv[2]

plot_as_one(data_path, output_file)
