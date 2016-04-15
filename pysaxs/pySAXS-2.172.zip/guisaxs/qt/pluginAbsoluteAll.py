# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2015
"""
import sys
from PyQt4 import QtGui, QtCore
'''import numpy
from scipy import interpolate
from guidata.dataset.datatypes import ActivableDataSet
from guidata.dataset.dataitems import FileOpenItem, BoolItem, ButtonItem
import guidata
import guidata.dataset.dataitems as di
import guidata.dataset.datatypes as dt
from  guidata.dataset import datatypes
from guidata.dataset import dataitems
from guidata.dataset.datatypes import DataSet, BeginGroup, EndGroup, ValueProp
from guidata.dataset.dataitems import BoolItem, FloatItem
from pySAXS.guisaxs.qt import plugin
from pySAXS.LS import background
from pySAXS.guisaxs import dataset
'''

from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgAbsoluteI

classlist=['AbsoluteAll'] #need to be specified

class AbsoluteAll(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="SAXS"
    subMenuText="Absolute all"
    icon="expand_selection.png"
    def execute(self):
        datalist=self.ListOfDatasChecked()
        
        #display the dialog box
        label=self.selectedData
        if self.selectedData is None:
            QtGui.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return
        #print self.data_dict[label].parameters
        #print label
        params=self.data_dict[label].parameters
        if params is not None:
            params.printout=self.printTXT
        reference=self.parent.referencedata
        #print 'reference data ',reference
        self.childSaxs=dlgAbsoluteI.dlgAbsolute(self,saxsparameters=params,\
                                                datasetname=label,printout=self.printTXT,referencedata=reference,\
                                                backgrounddata=self.parent.backgrounddata,datasetlist=datalist)
        #self.dlgFAI=dlgQtFAI.FAIDialog(self.parent)
        self.childSaxs.show()
    
    '''def execute(self):
        backgroundlist=["NO"]
        if self.parent.backgrounddata is not None:
             backgroundlist.append(self.parent.backgrounddata)
        reflist=["NO"]
        if self.parent.referencedata is not None:
             reflist.append(self.parent.referencedata)
        
        items = {
                 
        "thickness": dataitems.FloatItem("Thickness : ",1,unit='cm'),
        "backgroundData":dataitems.ChoiceItem("Substract ackground data : ",backgroundlist),
        "referenceData":dataitems.ChoiceItem("Substract reference data : ",reflist),
        }
        clz = type("Absolute Intensities for all :", (datatypes.DataSet,), items)
        self.form = clz()
        if self.form.edit():
            #ok
            self.calculate()
            
    def calculate(self):
        datalist=self.ListOfDatasChecked()
        self.thickness=self.form.thickness
        self.backgroundData=datalist[self.form.backgroundData]
    '''