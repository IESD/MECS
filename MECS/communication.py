"""Establishing connection with server, writing ssh public key"""

import os
import logging
import subprocess
import glob
import shutil

log = logging.getLogger(__name__)

class UploadFailed(Exception): pass

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
        if not has_key():
            return
        log.debug(f"Sending public key to server")
        # try:
        result = subprocess.run(["ssh-copy-id", f"-p {self.port}", f"{self.username}@{self.host}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode:
            log.warning("A problem occurred when attempting to register public key")
            log.error(result.stderr)
        else:
            log.info("registration successful")

    def create_remote_folder(self, folder_name):
        result = subprocess.run(["ssh", f"-p {self.port}", f"{self.username}@{self.host}", f"mkdir -p {self.data_root}/{folder_name}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode:
            log.warning("A problem occurred when attempting to create a remote folder")
            log.error(result.stderr)
        else:
            log.info(f"folder {folder_name} created on server")

    def copy_to_server(self, file, destination):
        result = subprocess.run(["scp", file, f"{self.username}@{self.host}:{destination}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode:
            log.warning("A problem occurred when attempting to copy a file to server")
            log.error(result.stderr)
            raise UploadFailed
        else:
            log.info(f"Copied {file} to {destination} on {self.host}")


    def upload(self, source_folder, destination_folder, archive_folder):
        """This pushes all the aggregated data up to the server and then archives the data"""
        files = sorted(glob.glob(os.path.join(source_folder, "*.json")))
        if not files:
            log.info("No files to upload")
        for file in files:
            path, fname = os.path.split(file)
            destination_file = os.path.join(self.data_root, destination_folder, fname)
            try:
                self.copy_to_server(file, destination_file)
            except UploadFailed:
                pass
            else:
                shutil.move(file, os.path.join(archive_folder, fname))
                log.info(f"Moved {file} to {archive_folder}")
