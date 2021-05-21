"""Establishing connection with server, writing ssh public key"""

import os
import logging
import subprocess

log = logging.getLogger(__name__)

def register(port, username, host):
    ssh_folder = os.path.expanduser("~/.ssh")
    has_key = lambda: os.path.exists(ssh_folder) and "id_rsa" in os.listdir(ssh_folder)
    if not has_key():
        subprocess.run(['ssh-keygen'])
    else:
        log.debug(f"SSH key exists in {ssh_folder}")
    if has_key():
        subprocess.run(["ssh-copy-id", f"-p {port}", f"{username}@{host}"], check=True)
