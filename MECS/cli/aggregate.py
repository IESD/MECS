"""Triggered via mecs-aggregate
Loads paths from config file
Calls MECS.data_management.aggregate.aggregate
"""
import logging
import os

from .. import __version__
from ..config import conf
from ..data_management.aggregate import aggregate as agg

log = logging.getLogger(__name__)


def aggregate():
    log.debug(f"MECS v{__version__} aggregating data")
    ROOT = os.path.expanduser(conf.get('MECS', 'root_folder'))
    OUTPUT_FOLDER = os.path.join(ROOT, conf.get('MECS', 'output_folder'))
    AGGREGATED_FOLDER = os.path.join(ROOT, conf.get('MECS', 'aggregated_folder'))
    agg(OUTPUT_FOLDER, AGGREGATED_FOLDER)
