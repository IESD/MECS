
import logging
import os
from configparser import NoOptionError

from .. import __version__, update_mecs
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
