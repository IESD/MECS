import logging
import os
import json
from collections import OrderedDict

from .. import MECSError
from ..data_acquisition.board import MECSBoard

log = logging.getLogger(__name__)


def get_devices_config(conf):
    devices_config_path = os.path.expanduser(conf.get('MECS', 'devices_config_path'))
    with open(devices_config_path) as f:
        devices_config = json.load(f)
    return devices_config

def get_board(conf):
    devices_config = get_devices_config(conf)
    hardware_required = conf.getboolean('MECS', 'hardware_required', fallback=True)
    try:
        return MECSBoard(hardware_required, **devices_config)
    except MECSError as exc:
        log.warning("Exiting, could not create MECSBoard")
        log.exception(exc)
        exit(0)
    except Exception as exc:
        log.warning("Unexpected Error!")
        log.exception(exc)
        exit(0)

def pretty_print(dict, heading=True):
    """
    Utility function for printing data to console
    Requires a dict-like containing the data
    Defaults to treating the first element as a heading
    So its best to use an OrderedDict
    """
    l1 = max([len(k) for k in dict.keys()])
    l2 = max([len(str(v)) for v in dict.values()])
    print()
    print("*" * (l1 + l2 + 6))
    for k, v in dict.items():
        print(f"* {k:>{l1}}: {v:<{l2}} *")
        if heading:
            print("*" * (l1 + l2 + 6))
            heading = False
    print("*" * (l1 + l2 + 6))

def prepare_output(data):
    """internal function to reorganise data into an ordered dict for printing"""
    output = OrderedDict({k: str(v) for k, v in data['data'].items()})
    output['dt'] = data['dt'].strftime("%Y-%m-%d %H:%M:%S")
    output.move_to_end('dt', last=False)
    return output

def print_output(board, clear=False):
    data = board.readings()
    output = prepare_output(data)
    if clear:
        os.system('clear')
    pretty_print(output)
