from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants
import zmq
import umsgpack




class Abridge():
    def __init__(self, board):
        self.board = board

    def cb(self,data):
        print(data)

    def do_command(self, msg):
        x = umsgpack.unpackb(msg)
        board.set_pin_mode(int(x['pin']), x['mode'], self.cb)



command = "digital_pin_mode"
# board = request.match_info.get('board')
enable = 'enable'
pin = '12'
mode = Constants.INPUT
command_msg = umsgpack.packb({u"command": command, u"enable": enable, u"pin": pin, u"mode": mode})

board = PyMata3()
bridge = Abridge(board)
bridge.do_command(command_msg)
while True:
    board.sleep(1)