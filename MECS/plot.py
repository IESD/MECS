"""
plotting raw data as images using matplotlib
"""
import logging
import glob
import os.path

import pandas as pd
from matplotlib import pyplot as plt

log = logging.getLogger(__name__)

def plot_file(data_path, image_path):
    log.debug(f"Loading data from {data_path}")
    df = pd.read_json(data_path, orient="split")
    cols = df.columns
    fig, axes = plt.subplots(4, 2, figsize=(14, 8))
    for i, (c, ax) in enumerate(zip(cols, axes.flatten())):
        log.debug(f"Plotting {c}")
        ax.plot(df[c], label=c, lw=1, color=f"C{i}")
        ax.legend()
    plt.tight_layout()
    log.info(f"Creating {image_path}")
    plt.savefig(image_path, dpi=300)

def plot_all(source_folder, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    files = sorted(glob.glob(os.path.join(source_folder, "*.json")))
    if not files:
        log.info("No files to plot")
    for source_file in files:
        path, fname = os.path.split(source_file)
        name, ext = os.path.splitext(fname)
        destination_file = os.path.join(dest_folder, f"{name}.png")
        plot_file(source_file, destination_file)
