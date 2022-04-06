
import logging
import os
import subprocess
from configparser import NoOptionError

from .. import __version__
from ..config import conf, args

log = logging.getLogger(__name__)

def update():
    log.debug(f"MECS v{__version__} updating installation")
    try:
        FULL_INSTALL = conf.getboolean('git', 'install', fallback=False)
        GIT_PATH = os.path.expanduser(conf.get('git', 'source_folder'))
        GIT_BRANCH = os.path.expanduser(conf.get('git', 'branch'))
    except NoOptionError as exc:
        log.warning(args.conf)
        log.error(exc)
        log.warning("required for code update")
        exit(0)
    update_mecs(GIT_PATH, GIT_BRANCH, full=FULL_INSTALL)



def update_mecs(path, branch, full=False):
    """This function will:
        ping google to restart comms
        pull the latest commits from github
        run setup.py to reinstall the software
    """
    os.chdir(path)
    ping_stat = subprocess.run(
        ["ping", "8.8.8.8","-w","5"], 
        capture_output=True,
        text=True
    )
    if ping_stat.returncode != 0:
        log.warning('Ping did not exit cleanly, outside network connectivity lost?')
        log.warning('StdOut:' + ping_stat.stdout)
        log.warning('StdErr:' + ping_stat.stderr)
    subprocess.run(["git", "pull", "origin", branch])
    subprocess.run(["python3", "setup.py", "install" if full else "develop"])

