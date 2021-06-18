import os.path

from MECS.data_acquisition import MECSBoard

bit_rate = 16
impedance = 16800
calibration = os.path.expanduser("~/calibration.ini")

board = MECSBoard(bit_rate, impedance, calibration)

print(board.readings())
