"""miRNA Python Library

a collection of modules for dealing with microRNA data in Python.

"""

__version__ = "0.1.0"
__author__ = "kulwadee"

__all__=["UI","Utility"]

def info():
   return ("miRNA Python Libray, version %s" % __version__)

import os
import sys
import xml.etree.cElementTree
import subprocess


from pymirna.UI.MainPage import *
from pymirna.UI.PreProcessUI import *
from pymirna.UI.PreProcessUI import *
from pymirna.Utility import *
from pymirna.UI.SelectInputDialog import *

def runApp():
    app = w.QApplication([])
    app.setApplicationName("miRWB")
    mainpage = MainPage()
    mainpage.show()
    sys.exit(app.exec_())
