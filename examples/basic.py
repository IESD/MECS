"""
The CLI scripts are convenient but inflexible
This is an example of how to use the MECSBoard directly
Its pretty simple
"""
import os
import time
import pprint

# we only really need the MECSBoard class
from MECS.data_acquisition import MECSBoard

# initialise the board
board = MECSBoard(16, 16800, "/home/pi/calibration.ini")
while(True):
    readings = board.readings()
    os.system('clear')
    pprint.pprint(readings)
    time.sleep(0.1)
