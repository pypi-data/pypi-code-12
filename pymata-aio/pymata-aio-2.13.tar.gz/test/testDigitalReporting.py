from pymata_aio.constants import Constants
from pymata_aio.pymata3 import PyMata3

board = PyMata3()
board.set_pin_mode(13, Constants.INPUT)
x = board.digital_read(13)
board.disable_digital_reporting(13)
print ('A ' + str(x))
print('change')
board.sleep(5)

x = board.digital_read(13)
print ('B ' + str(x))
board.sleep(2)
board.enable_digital_reporting(13)
print( "Change2")
board.sleep(5)
x = board.digital_read(13)
print ('C ' + str(x))
board.sleep(2)
