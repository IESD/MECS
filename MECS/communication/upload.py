import os
import logging
import subprocess

log = logging.getLogger(__name__)

def copy_to_server(file, destination, username, host):
    subprocess.run(["scp", file, f"{username}@{host}:{destination}"])

def create_remote_folder(folder_name, username, host):
    # print("ssh", f"{username}@{host}", f"'mkdir -p data/{folder_name}'")
    subprocess.run(["ssh", f"{username}@{host}", f"mkdir -p data/{folder_name}"])
