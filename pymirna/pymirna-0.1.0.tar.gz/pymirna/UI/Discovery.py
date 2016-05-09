import PyQt5.QtWidgets as w
from PyQt5.QtCore import *
import pymirna.UI.SettingBlock as s
from pymirna.UI.mComboBox import *

from pymirna.UI.DiscoveryToolBlock import *
from pymirna.UI.WorkflowUI import *

class Discovery(WorkflowUI):

    def __init__(self, p):
        super(Discovery, self).__init__(p)

    def _addTool(self):
        pptb = DiscoveryToolBlock(self, [self._initID, self._toolcount])
        pptb.setParent(self._vscrollContent)
        self._vscrollLayout.addWidget(pptb)
        pptb.show()
        print(self._vscrollLayout.count())
        self._toolQueue.append(pptb)
        self._initID += 1
        self._toolcount += 1