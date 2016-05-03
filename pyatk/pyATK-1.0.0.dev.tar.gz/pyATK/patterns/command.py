
from pyATK.utils.decorators import not_implemented

class AbstractCommand:

    @not_implemented
    def __init__(self):
        pass

    @not_implemented
    def execute(self):
        pass

    @not_implemented
    def undo(self):
        pass
