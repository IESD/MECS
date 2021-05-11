"""
Module for initialisation

Here we set up the basic things we need to do before the system will be fully operational

1. Create an identifier for the device based on MAC address.

"""

import os
import sys
import subprocess
import logging
import logging.config
from configparser import ConfigParser

def identifier():
    pass

def initialise(config):
    log.info("Initialising")
    for c in config:
        log.debug(f"{c}: {config[c]}")
    has_key = lambda: "id_rsa" in os.listdir(config["ssh_folder"])
    if not has_key():
        subprocess.run(['ssh-keygen'])
    else:
        log.info(f"Key exists in {config["ssh_folder"]}")
    if has_key():
        try:
            subprocess.run(["ssh-copy-id", f"-p {config['port']}", f"{config['username']}@{config['host']}"], check=True)
        except subprocess.CalledProcessError as ex:
            log.error(ex)
            exit()



if __name__ == "__main__":
    # configuration from file
    try:
        config_file = sys.argv[1]
    except IndexError:
        config_file = "./MECS.ini"

    config = ConfigParser()

    if not os.path.exists(config_file):
        print(f"Error: configuration file {config_file} not found")
        exit(1)
    config.read(config_file)
    logging.config.fileConfig(config)
    log = logging.getLogger(__name__)
    initialise(config["MECS"])
