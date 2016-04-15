# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2013
"""
import sys
from PyQt4 import QtGui, QtCore
import numpy
from scipy import interpolate
from pySAXS.guisaxs.dataset import *
from pySAXS.guisaxs.qt import dlgCalculatorui

class dlgCalculator(QtGui.QDialog,dlgCalculatorui.Ui_Calculator):
    def __init__(self,parent,datalist=None,newname='newname'):
        QtGui.QDialog.__init__(self)
        self.parentwindow=parent
        self.listofdata=datalist
        # Set up the user interface from Designer.
        self.setupUi(self)
        self.EditNewName.setText(newname)
        self.EditFormula.setText("i0*1")
        txt=""
        i=0
        self.variableDict={}#-- generate variableDict
        for label in datalist:
            txt+="i"+str(i)+" = "+label+"\n"
            self.variableDict["i"+str(i)]=label
            i+=1
        self.lblVariables.setText(txt)
        
        
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Calculator.accept)
        #QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Calculator.reject)
        self.btnApply.clicked.connect(self.OnApply)
        self.btnQuit.clicked.connect(self.reject)
    
    def OnApply(self):
        newdatasetname=str(self.EditNewName.text())
        formula=str(self.EditFormula.text())
        
        newdatasetname=self.parentwindow.cleanString(newdatasetname)
        
        qref=numpy.copy(self.parentwindow.data_dict[self.listofdata[0]].q)
        
        #--
        #print newdatasetname,formula,variableDict
        formulaForComment=formula
        for var in self.variableDict.keys():
            formulaForComment=formulaForComment.replace(var,self.variableDict[var])
            self.parentwindow.printTXT(formulaForComment)
        newdict={}
        newerror=numpy.zeros(numpy.shape(qref))
        
        #--convert variableDict
        for var in self.variableDict:
            name=self.variableDict[var]
            #print name
            if not(self.parentwindow.data_dict.has_key(name)):
                print "error on mainGuisaxs.OnEditCalculator"
                return
            #variableDict contain variable name and dataset name
            i=self.parentwindow.data_dict[name].i
            q=self.parentwindow.data_dict[name].q
            if str(q)<>str(qref):
                self.parentwindow.printTXT("trying interpolation for ",name)
                newf=interpolate.interp1d(q,i,kind='linear',bounds_error=0)
                newi=newf(qref)
            else:
                newi=i
                #addition for errors
                error=self.parentwindow.data_dict[name].error
                if error!=None and newerror!=None:
                    newerror+=error
                else:
                    newerror=None
            newdict[var]=newi
        #--evaluate
        self.parentwindow.printTXT("trying evaluation of ",formula)
        
        safe_list = ['math','acos', 'asin', 'atan', 'atan2', 'ceil', 'cos', 'cosh', 'degrees', \
                     'e', 'exp', 'fabs', 'floor', 'fmod', 'frexp', 'hypot', 'ldexp', 'log',\
                     'log10', 'modf', 'pi', 'pow', 'radians', 'sin', 'sinh', 'sqrt', 'tan', 'tanh'] #use the list to filter the local namespace safe_dict = dict([ (k, locals().get(k, None)) for k in safe_list ])
        for k in safe_list:
            newdict[k]=locals().get(k)
        
        iout=numpy.array(eval(formula,newdict))
        self.parentwindow.data_dict[newdatasetname]=dataset(newdatasetname,qref,iout,comment=formulaForComment,type='calculated',error=newerror)#[data[0], data[1], datafilename, True]
        self.parentwindow.redrawTheList()
        self.parentwindow.Replot()
    
    def getValues(self):
        return str(self.EditNewName.text()), str(self.EditFormula.text()),self.variableDict
