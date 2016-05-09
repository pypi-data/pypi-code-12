from PyQt5.QtWidgets import *
from pymirna.UI.mComboBox import *
from pymirna.UI.CutadaptUI import *
from pymirna.UI.ToolBlock import *
from pymirna.UI.FastxUI import *

FASTQTOFASTA = "fastq to fasta"
CUTADAPT = "Cutadapt"


class PreProcessingToolBlock(ToolBlock):
    def __init__(self, ppui, count):
        super(PreProcessingToolBlock, self).__init__(ppui, count)

        self._workflowStep = PREPROCESSING
        self._algorithmCombobox.addItem(CUTADAPT)
        self._algorithmCombobox.addItem(FASTQTOFASTA)

    def ChangeWidget(self):
        print("Widget Count : "+str(self._vboxlayout.count()))

        if(self._algorithmCombobox.getData() == "None"):
            widget = self._vboxlayout.takeAt(self._vboxlayout.count()-1).widget()
            widget.setVisible(False)
            widget = None
            self._vboxlayout.addWidget(QWidget())
            self._vboxlayout.update()
            self._curalgo = None
        elif(self._algorithmCombobox.getData() == CUTADAPT):
            widget = self._vboxlayout.takeAt(self._vboxlayout.count()-1).widget()
            widget.setVisible(False)
            ca = CutadaptUI(self, self.getID())
            self._vboxlayout.addWidget(ca)
            self._curalgo = ca
            self._vboxlayout.update()

        elif(self._algorithmCombobox.getData() == FASTQTOFASTA):
            widget = self._vboxlayout.takeAt(self._vboxlayout.count()-1).widget()
            widget.setVisible(False)

            ca = FastqtoFasta(self, self.getID())
            self._vboxlayout.addWidget(ca)
            self._curalgo = ca
            self._vboxlayout.update()

