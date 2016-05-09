import PyQt5.QtWidgets as w


class mComboBox(w.QComboBox):

    def __init__(self):
        super(mComboBox, self).__init__()

    def getData(self):
        return self.currentText()

    def setData(self, value):
        for i in eval(self.count()):
            if(value == self.itemData(i)):
                self.setCurrentIndex(i)
                return
        print(value+" not found in the combobox")

