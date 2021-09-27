import logging
import time

from .. import __version__, MECSError
from ..config import conf

from .utils import get_board, print_output

log = logging.getLogger(__name__)


def get_readings_function():
    try:
        board = get_board(conf)
    except MECSError as exc:
        log.warning("Exiting, could not create MECSBoard")
        log.exception(exc)
        exit(0)
    except Exception as exc:
        log.warning("Unexpected Error!")
        log.exception(exc)
        exit(0)
    return board.readings


def test():
    log.debug(f"MECS v{__version__} testing data")
    board = get_board(conf)
    print_output(board, clear=False)


def test2():
    log.debug(f"MECS v{__version__} continuously testing data")
    board = get_board(conf)
    try:
        while(True):
            print_output(board, clear=True)
            print("ctrl + C to exit")
            time.sleep(2)
    except KeyboardInterrupt:
        pass
