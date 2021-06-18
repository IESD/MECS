"""
This is an example of how to use the MECS library without the cli tooling
"""
import logging

# we only need the MECSBoard class
from MECS.data_acquisition import MECSBoard

# initialise logging to see the log messages
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# initialise the board
board = MECSBoard(16, 16800, "/home/pi/calibration.ini")

# get some readings and log them
readings = board.readings()
for key, value in readings.items():
    log.info(f"{key}: {value}")
