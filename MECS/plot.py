"""
plotting raw data as images using matplotlib
"""
import logging
import glob
import os.path

import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates

log = logging.getLogger(__name__)

def plot_file(data_path, image_path):
    log.debug(f"Loading data from {data_path}")
    df = pd.read_json(data_path, orient="split")
    plot_frame(df, image_path)

def plot_frame(df, image_path):
    cols = df.columns
    fig, axes = plt.subplots(4, 3, figsize=(14, 8))
    fig.suptitle(f"MECS data for file {data_path}")
    for i, (c, ax) in enumerate(zip(cols, axes.flatten())):
        log.debug(f"Plotting {c}")
        ax.plot(df[c], label=c, lw=1, color=f"C{i}")
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.tick_params(axis='x', labelrotation=45)
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

def plot_as_one(source_folder, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    dfs = []
    files = sorted(glob.glob(os.path.join(source_folder, "*.json")))
    for source_file in files:
        dfs.append(pd.read_json(source_file, orient="split"))
    destination_file = os.path.join(dest_folder, f"ALL.png")
    df = pd.concat(dfs)
    plot_frame(df, destination_file)
