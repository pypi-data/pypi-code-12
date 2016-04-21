__author__ = 'afy'
from pymata_aio.pymata3 import PyMata3
from pymata_aio.constants import Constants


class TestMe:
    board = PyMata3(2)
    result = None

    def my_callback(self, data):
        self.result = data
        # print(self.result)

    # set pot to maximum to pass and anything else to fail
    def test_analog_read_write(self):
        # have a potentiometer on A2 and set it to max
        self.board.set_pin_mode(2, Constants.ANALOG)
        self.board.sleep(1)
        av = self.board.analog_read(2)
        assert av == 1023