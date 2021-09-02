import sys

sys.argv = ['', '-c', '/home/graeme/.MECS/newconf.ini']
from MECS.config import conf
from MECS.data_acquisition.board import MECSBoard
board = MECSBoard(conf)

r = board.readings()
print(board)
print(r)
