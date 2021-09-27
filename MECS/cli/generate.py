"""Triggered via mecs-generate
Loads paths from config file
Calls MECS.data_management.generate.generate
"""

import logging
import os

from .. import __version__
from ..config import conf
from ..data_management.generate import generate as gen

from .utils import get_board

log = logging.getLogger(__name__)


def generate():
    log.debug(f"MECS v{__version__} generating data")
    ROOT = os.path.expanduser(conf.get('MECS', 'root_folder'))
    OUTPUT_FOLDER = os.path.join(ROOT, conf.get('MECS', 'output_folder'))
    board = get_board(conf)
    gen(OUTPUT_FOLDER, board.readings)
