"""
The CLI scripts are convenient but inflexible
This is an example of how to use the MECSBoard directly
Its pretty simple
"""
import logging
import pprint

# we only really need the MECSBoard class
from MECS.data_acquisition import MECSBoard

# optionally initialise logging to see the log messages
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# initialise the board
board = MECSBoard(16, 16800, "/home/pi/calibration.ini")
while(True):
    os.system('clear')
    pprint.pprint(board.readings())
    time.sleep(0.1)
