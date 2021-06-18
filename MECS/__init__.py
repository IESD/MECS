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

__version__ = pkg_resources.get_distribution('MECS').version

class MECSError(Exception): pass
class MECSConfigError(MECSError): pass
class MECSHardwareError(MECSError): pass


def update_mecs(path, branch, full=False):
    """This function will:
        pull the latest commits from github and
        run setup.py to reinstall the software
    """
    os.chdir(path)
    subprocess.run(["git", "pull", "origin", branch])
    subprocess.run(["python3", "setup.py", "install" if full else "develop"])
