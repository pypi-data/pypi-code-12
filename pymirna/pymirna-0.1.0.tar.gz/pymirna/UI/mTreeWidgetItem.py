from PyQt5 import QtWidgets as w


FILE = 1
FOLDER = 2
PROJECT = 3

class mTreeWidgetItem(w.QTreeWidgetItem):
    def __init__(self, p, lis, fpath, t):
        super(mTreeWidgetItem, self).__init__(p)
        self.__fpath = fpath
        self.__name = lis[0]
        self.setText(0, self.__name)

        if(t < 1 or t > 3):
            t = 1
        self.__type = t

    def getFilePath(self):
        return self.__fpath+self.__name

    def setType(self, t):
        if(t < 1 or t > 3):
            t = 1
            self.__type = t

    def getType(self):
        return self.__type

    def getName(self):
        return self.__name