from PyQt5.QtWidgets import *
from pymirna.UI.mComboBox import *
from pymirna.UI.CutadaptUI import *
from pymirna.UI.ToolBlock import *

class DiscoveryToolBlock(ToolBlock):
    def __init__(self, ppui, count):
        super(DiscoveryToolBlock, self).__init__(ppui, count)
        self._workflowStep = DISCOVERY
        self._algorithmCombobox.addItem("mirDeep2")


    def ChangeWidget(self):
        print("Widget Count : "+str(self.__vboxlayout.count()))

        if(self.__algorithmCombobox.getData() == "None"):
            widget = self.__vboxlayout.takeAt(self.__vboxlayout.count()-1).widget()
            widget.setVisible(False)
            widget = None
            self.__vboxlayout.addWidget(QWidget())
            self.__vboxlayout.update()
            self.__curalgo = None
        elif(self.__algorithmCombobox.getData() == "mirDeep2"):
            widget = self.__vboxlayout.takeAt(self.__vboxlayout.count()-1).widget()
            widget.setVisible(False)

            #TODO CHANGE THIS
            ca = CutadaptUI(self)
            self.__vboxlayout.addWidget(ca)
            self.__curalgo = ca
            self.__vboxlayout.update()

