import logging
from pathlib import Path
import copy
import json

from .. import __version__
from ..config import conf

from .utils import get_board, get_devices_config

log = logging.getLogger(__name__)

def calibrate():
    log.debug(f"MECS v{__version__} calibrating current sensors")

    CALIBRATION_SAMPLES = conf.getint('MECS', 'calibration_samples', fallback=25)
    CALIBRATION_PATH = Path(conf.get('MECS', 'devices_config_path')).expanduser()

    original_config = get_devices_config(conf)
    new_config = copy.deepcopy(original_config)
    board = get_board(conf)

    for label, config in board.calibrate(CALIBRATION_SAMPLES):
        log.info(f"updating configuration data for [{label}]")
        new_config[label] = config

    confirm = f"Overwrite existing configuration file? (y/n) "
    if input(confirm).lower() != "y":
        return

    original_path = Path(CALIBRATION_PATH)
    backup_path = Path(f"{CALIBRATION_PATH}.bkp")
    log.info(f"Making backup of config at {backup_path}")
    with backup_path.open('w') as f:
        json.dump(original_config, f, indent=2)
    with original_path.open('w') as f:
        json.dump(new_config, f, indent=2)
