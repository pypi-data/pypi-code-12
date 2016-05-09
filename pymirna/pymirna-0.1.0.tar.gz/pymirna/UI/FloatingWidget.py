__author__ = 'haru'

import PyQt5.QtWidgets as w
import PyQt5.QtCore as c


class FloatingWidget(w.QWidget):

    def __init__(self, title = "Floating Windows", width = 640, height = 480):
        super(FloatingWidget, self).__init__()
        self.setWindowTitle(title)
        self.setFixedSize(width, height)


    def __initAttribute__(self):
        Attributegoeshere = "Test"
