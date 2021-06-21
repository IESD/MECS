"""
Here we access a single analogue channel
"""
import os
import time
import pprint

from MECS.data_acquisition import MECSBoard

board = MECSBoard(16, 16800, "/home/pi/calibration.ini")
while(True):
    PM2_5, PM10 = board.get_particulates()
    os.system('clear')
    print(f"PM2_5: {PM2_5}, PM10: {PM10}")
    time.sleep(0.02)
