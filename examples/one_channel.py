"""
Here we access a single analogue channel
"""
import os
import time
import pprint

# we only really need the MECSBoard class
from MECS.data_acquisition import MECSBoard

# initialise the board
board = MECSBoard(16, 16800, "/home/pi/calibration.ini")
while(True):
    reading = board.analogue_reading('battery_voltage')
    os.system('clear')
    print(f"battery_voltage: {reading}")
    time.sleep(0.02)
