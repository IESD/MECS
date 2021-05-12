"""
Module for initialisation

Here we set up the basic things we need to do before the system will be fully operational

1. Create an identifier for the device based on MAC address if it doesn't already exist.
2. Create ssh public/private key pair if it doesn't already exist
3. Upload public key to the server if we have one

"""

import os
import subprocess
import logging
import uuid

from .config import config, config_file

conf = config()
log = logging.getLogger(__name__)

def write_identifier(conf, force=False):
    """write unique identifier into config file"""
    if force or ("data_acquisition_id" not in conf['MECS']):
        identifier = hex(uuid.getnode())
        conf.set('MECS', 'data_acquisition_id', identifier)
        path = config_file()
        with open(path, 'w') as f:
            conf.write(f)
        log.info(f"New data_acquisition_id based on MAC address: {identifier}")
    else:
        log.info(f"Existing data_acquisition_id: {conf['MECS']['data_acquisition_id']}")


def register(conf):
    has_key = lambda: "id_rsa" in os.listdir(conf['ssh_folder'])
    if not has_key():
        subprocess.run(['ssh-keygen'])
    else:
        log.debug(f"Key exists in {conf['ssh_folder']}")
    if has_key():
        subprocess.run(["ssh-copy-id", f"-p {conf['port']}", f"{conf['username']}@{conf['host']}"], check=True)

def main():
    log.debug("Initialising")
    write_identifier(conf)
    register(conf['MECS'])

if __name__ == "__main__":
    main()
