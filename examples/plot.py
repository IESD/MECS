import sys
from MECS.plot import plot_file

data_path = sys.argv[1]
output_path = sys.argv[2]

plot_file(data_path, output_path)
