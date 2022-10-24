import logging
from collections import OrderedDict
from datetime import datetime
from configparser import NoOptionError

from .. import __version__
from ..config import args, conf

from .utils import pretty_print

log = logging.getLogger(__name__)

def status():
    """a simple script to print out some key information"""
    UNIT_ID = conf.get('MECS', 'unit_id', fallback="unidentified")
    data = OrderedDict({
        "MECS version": __version__,
        "conf": args.conf,
        "UNIT_ID": UNIT_ID,
        "DT": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S (UTC)'),
    })
    try:
        USERNAME = conf.get('MECS-SERVER', 'username')
        HOST = conf.get('MECS-SERVER', 'host')
        PORT = conf.get('MECS-SERVER', 'port')
        data["Server"] = f"{USERNAME}@{HOST}:{PORT}"
    except NoOptionError as exc:
        pretty_print(data)
        log.warning(f"problem in configuration file {args.conf}")
        log.warning(exc)
        log.warning("required for server upload")
        log.warning("Run mecs-init to set the values")
    else:
        pretty_print(data)
