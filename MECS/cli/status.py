from collections import OrderedDict
from datetime import datetime

from .. import __version__
from ..config import args, conf

from .utils import pretty_print


def status():
    """a simple script to print out some key information"""
    UNIT_ID = conf.get('MECS', 'unit_id', fallback="unidentified")
    USERNAME = conf.get('MECS-SERVER', 'username')
    HOST = conf.get('MECS-SERVER', 'host')
    PORT = conf.get('MECS-SERVER', 'port')
    data = OrderedDict({
        "MECS version": __version__,
        "conf": args.conf,
        "UNIT_ID": UNIT_ID,
        "DT": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S (UTC)'),
        "Server": f"{USERNAME}@{HOST}:{PORT}"
    })
    pretty_print(data)
