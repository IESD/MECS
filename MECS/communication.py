"""Establishing connection with server, writing ssh public key"""

import os
import logging
import subprocess
import glob
import shutil

log = logging.getLogger(__name__)

class MECSServer:
    def __init__(self, username, host, port, data_root):
        self.username = username
        self.host = host
        self.port = port
        self.data_root = data_root

    def register(self):
        ssh_folder = os.path.expanduser("~/.ssh")
        has_key = lambda: os.path.exists(ssh_folder) and "id_rsa" in os.listdir(ssh_folder)
        if not has_key():
            subprocess.run(['ssh-keygen'])
            log.info(f"Created SSH key pair")
        else:
            log.debug(f"SSH key exists in {ssh_folder}")
        if has_key():
            log.debug(f"Sending public key to server")
            subprocess.run(["ssh-copy-id", f"-p {self.port}", f"{self.username}@{self.host}"], check=True)

    def create_remote_folder(self, folder_name):
        subprocess.run(["ssh", f"-p {self.port}", f"{self.username}@{self.host}", f"mkdir -p {self.data_root}/{folder_name}"])

    def copy_to_server(self, file, destination):
        log.info(f"attempting to copy {file} to {destination} on {self.host}")
        subprocess.run(["scp", file, f"{self.username}@{self.host}:{destination}"])

    def upload(self, source_folder, destination_folder, archive_folder):
        """This pushes all the aggregated data up to the server and then archives the data"""
        files = sorted(glob.glob(os.path.join(source_folder, "*.json")))
        for file in files:
            path, fname = os.path.split(file)
            destination_file = os.path.join(destination_folder, fname)
            self.copy_to_server(file, destination_file)
            shutil.move(file, os.path.join(archive_folder, fname))


# def register(port, username, host):
#     ssh_folder = os.path.expanduser("~/.ssh")
#     has_key = lambda: os.path.exists(ssh_folder) and "id_rsa" in os.listdir(ssh_folder)
#     if not has_key():
#         subprocess.run(['ssh-keygen'])
#         log.info(f"Created SSH key pair")
#     else:
#         log.debug(f"SSH key exists in {ssh_folder}")
#     if has_key():
#         log.debug(f"Copying public key to server, just in case")
#         subprocess.run(["ssh-copy-id", f"-p {port}", f"{username}@{host}"], check=True)

# def upload(source_folder, destination_folder, archive_folder):
#     """This pushes all the aggregated data up to the server and then archives the data"""
#     files = sorted(glob.glob(os.path.join(source_folder, "*.json")))
#     for file in files:
#         path, fname = os.path.split(file)
#         destination_file = os.path.join(destination_folder, fname)
#         copy_to_server(file, destination_file, username, host)
#         shutil.move(file, os.path.join(archive_folder, fname))

# def copy_to_server(file, destination, username, host):
#     subprocess.run(["scp", file, f"{username}@{host}:{destination}"])

# def create_remote_folder(folder_name, username, host):
#     subprocess.run(["ssh", f"{username}@{host}", f"mkdir -p data/{folder_name}"])
