
from pyATK.Cmd.Helpers.ColorHelper import Color
from pyATK.Cmd.Helpers.IOHelper import IOHelper
from pyATK.Cmd.Helpers.ProgressHelper import ProgressBarHelper
from pyATK.Cmd.Helpers.TableHelper import TableHelper


class Output:
    IO_HELPER = 0x01
    PROGRESS_HELPER = 0x02
    TABLE_HELPER = 0x04
    helpers = []

    def __init__(self):
        pass

    def write(self, msg, color=None):
        if color is None:
            print(msg)
        else:
            Color.colored(msg, color)

    def getHelper(self, name):
        return self.helpers[name]
