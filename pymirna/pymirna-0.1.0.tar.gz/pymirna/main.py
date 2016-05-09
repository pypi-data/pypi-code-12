__author__ = 'SupanatK'

import os
import sys
import xml.etree.cElementTree
import subprocess


from pymirna.UI.MainPage import *
from pymirna.UI.PreProcessUI import *
from pymirna.UI.PreProcessUI import *
from pymirna.Utility import *
from pymirna.UI.SelectInputDialog import *

if(__name__ == '__main__'):

    # TODO FINISH THIS IN TIME DUDE!!
    app = w.QApplication([])
    app.setApplicationName("miRWB")
    mainpage = MainPage()
    mainpage.show()
    sys.exit(app.exec_())