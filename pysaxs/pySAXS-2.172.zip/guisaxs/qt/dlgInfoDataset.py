# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2015
"""
import sys
from PyQt4 import QtGui, QtCore, uic
from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgAbsoluteI
from pySAXS.guisaxs import dataset
import pySAXS

class dlgInfoDataset(QtGui.QDialog):
    def __init__(self, dataset):
        
        QtGui.QDialog.__init__(self)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgInfoDataset.ui", self)
        self.ui.show()
        self.ui.labelDataset.setText(dataset.name)
        self.ui.labelQmin.setText("qmin : "+str(dataset.q[0]))
        self.ui.labelQmax.setText("qmax : "+str(dataset.q[-1]))
        if dataset.error is None:
            noerror=True
            headerNames = ["q", "i"]
        else:
            noerror=False
            headerNames = ["q", "i","error"]
        
        self.ui.tableWidget.setColumnCount(len(headerNames))
        self.ui.tableWidget.setRowCount(len(dataset.q))
        
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
                
        for i in range(len(dataset.q)):
            self.ui.tableWidget.setItem(i, 0, QtGui.QTableWidgetItem(str(dataset.q[i])))
            self.ui.tableWidget.setItem(i, 1, QtGui.QTableWidgetItem(str(dataset.i[i])))
            if not noerror:
                self.ui.tableWidget.setItem(i, 2, QtGui.QTableWidgetItem(str(dataset.error[i])))
        
        
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        
        
    def click(self,obj=None):
        name=obj.text()
        #print name
        if name=='OK':
            self.close()
        else:
            self.close()
            
        