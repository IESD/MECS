"""
This script could do a lot more
Perhaps check all necessary parameters and offer to fill them or update them
e.g. server details
this should be integrated with the default config files and make_mecs
"""
import logging

from .. import __version__

from ..config import args, conf, initialise_unit_id

log = logging.getLogger(__name__)


def initialise():
    log.debug(f"MECS v{__version__} initialising")
    initialise_unit_id(args.conf, conf)
