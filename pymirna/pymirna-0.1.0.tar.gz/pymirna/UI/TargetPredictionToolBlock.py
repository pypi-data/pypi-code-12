from PyQt5.QtWidgets import *
from pymirna.UI.mComboBox import *
from pymirna.UI.CutadaptUI import *
from pymirna.UI.ToolBlock import *
from pymirna.UI.miRandaUI import *
from pymirna.UI.FastxUI import *

MIRANDA = "miRanda"

class TargetPredictionToolBlock(ToolBlock):
    def __init__(self, ppui, count):
        super(TargetPredictionToolBlock, self).__init__(ppui, count)

        self._workflowStep = TARGETPREDICTION
        self._algorithmCombobox.addItem(MIRANDA)

    def ChangeWidget(self):
        print("Widget Count : "+str(self._vboxlayout.count()))

        if(self._algorithmCombobox.getData() == "None"):
            widget = self._vboxlayout.takeAt(self._vboxlayout.count()-1).widget()
            widget.setVisible(False)
            widget = None
            self._vboxlayout.addWidget(QWidget())
            self._vboxlayout.update()
            self._curalgo = None
        elif(self._algorithmCombobox.getData() == MIRANDA):
            widget = self._vboxlayout.takeAt(self._vboxlayout.count()-1).widget()
            widget.setVisible(False)

            #TODO CHANGE THIS
            ca = MirandaUI(self, self.getID())
            self._vboxlayout.addWidget(ca)
            self._curalgo = ca
            self._vboxlayout.update()



