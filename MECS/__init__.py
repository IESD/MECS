"""
MECS is a system for monitoring sensors attached to a raspberry pi
It includes packages for:
    data acquisition from the sensors
    managing data locally
    uploading data to a server
"""

import pkg_resources
import subprocess
import os

import logging

log = logging.getLogger(__name__)

__version__ = pkg_resources.get_distribution('MECS').version

class MECSError(Exception): pass
class MECSConfigError(MECSError): pass
class MECSHardwareError(MECSError): pass


def update_mecs(path, branch, full=False):
    """This function will:
        ping google to restart comms
        pull the latest commits from github
        run setup.py to reinstall the software
    """
    os.chdir(path)
    ping_stat = subprocess.run(["ping", "8.8.8.8","-w","5"], capture_output=True)
    if ping_stat.returncode != 0:
        log.warning('Ping did not exit cleanly, outside network connectivity lost?')
        log.warning('StdOut:' + ping_stat.stdout)
        log.warning('StdErr:' + ping_stat.stderr)
    subprocess.run(["git", "pull", "origin", branch])
    subprocess.run(["python3", "setup.py", "install" if full else "develop"])

