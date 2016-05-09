import PyQt5.QtWidgets as w


class SettingBlock (w.QHBoxLayout):



    def __init__(self, labelName, relement = None):
        super(SettingBlock, self).__init__()
        self.__initAttribute__(labelName)
        if(relement is not None or relement is not w.QWidget ):
            self.__rightelement = relement
            self.addWidget(self.__rightelement)


    def __initAttribute__(self, labelName):
        self.__label = w.QLabel(labelName)
        self.addWidget(self.__label)
        self.__rightelement = None

    def addWidgetToLayout(self, widget):
        if(self.__rightelement == None):
            self.__rightelement = widget
            self.addWidget(self.__rightelement)

        elif(self.__rightelement is not None):
            temp = self.__rightelement
            self.__rightelement = []
            self.__rightelement.append(temp)
            self.addWidget(widget)
            self.__rightelement.append(widget)

        elif(type(self.__rightelement) == list):
            self.addWidget(widget)
            self.__rightelement.append(widget)

    def checkIdentity(self, id):
        if(id == self.__label.text()):
            return True
        return False

    def getData(self):
        if(type(self.__rightelement) == list):
            lis = []
            for _ in self.__rightelement:
                lis.append(self.__rightelement.getData())
            return lis
        return self.__rightelement.getData()

    def setData(self, value):
        if(type(value) == list):
            for i in value:
                self.__rightelement.setData(i)
        else:
            self.__rightelement.setData(value)

    def changeIdentity(self, name):
        if(len(name) == 0):
            return
        self.__label.setText(name)