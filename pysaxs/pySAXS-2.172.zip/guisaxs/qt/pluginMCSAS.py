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
from pySAXS.mcsas import MCtools
from time import sleep
import numpy
from matplotlib.pyplot import bar
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar


classlist=['MCsas'] #need to be specified

class MCsas(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="MC SAS"
    subMenuText="Start MC"
    icon="mcsas.ico"
    def execute(self):
        datalist=self.ListOfDatasChecked()
        
        #display the dialog box
        label=self.selectedData
        if self.selectedData is None:
            QtGui.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return
        #print self.data_dict[label].parameters
        #print label
        
        self.dlg=dlgMCSAS(self.selectedData,self.parent)
        
    

class dlgMCSAS(QtGui.QDialog):
    def __init__(self, selectedData,parent):
        self.selectedData=selectedData
        self.parent=parent
        datas=self.parent.data_dict[self.selectedData]
        q=numpy.array(datas.q)*10
        QtGui.QDialog.__init__(self, parent)
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgMCsas.ui", self)
        self.ui.show()
        self.ui.labelDataset.setText(str(selectedData))
        self.ui.editNbSpheres.setText(str(300))
        self.ui.editNbIter.setText(str(5))
        self.ui.editHistBin.setText(str(50))
        self.ui.editLowLim.setText(str(numpy.pi/numpy.max(q)))
        self.ui.editHighLim.setText(str(numpy.pi/numpy.min(q)))
        self.ui.progressBar.setMaximum(300)
        self.ui.progressBar.setValue(0)
        self.hscale='lin'
        self.ui.labelCredits.setText('Small programs for Monte-Carlo fitting of SAXS patterns.\n'+\
                                     'It is released under a Creative Commons CC-BY-SA license. \n'+\
                                     'Please cite as:\n'+\
                                     'Brian R. Pauw, 2012, http://arxiv.org/abs/1210.5304 arXiv:1210.5304.')
        #self.fig2=self.ui.matplotlibwidget.figure
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        self.ui.navi_toolbar = NavigationToolbar(self.ui.matplotlibwidget, self)
        self.ui.verticalLayout_2.insertWidget(0,self.ui.navi_toolbar)
        
        ''''x=numpy.arange(100)
        y=numpy.sin(x)
        self.plt2=self.fig2.add_subplot(111) 
        self.plt2.plot(x,y)
        self.ui.matplotlibwidget.draw()
        '''
    def click(self,obj=None):
        name=obj.text()
        print name
        if name=='Close':
            self.close()
        elif name=='OK':
            
            self.startMC()
            
    def updateUI(self,nr):
        self.ui.progressBar.setValue(nr)
    
    def startMC(self):
        datas=self.parent.data_dict[self.selectedData]
        q=numpy.array(datas.q)*10
        I=numpy.array(datas.i)
        E=numpy.array(datas.error)
        #print E
        q=q[numpy.nonzero(I)]
        itemp=I[numpy.nonzero(I)]
        '''print numpy.nonzero(I)
        print len(E)
        print len(I)'''
        E=E[numpy.nonzero(I)]
        I=itemp
        '''self.plt2=self.fig2.add_subplot(111) 
        self.plt2.plot(q,I)
        #self.axes.hold(True)
        
        self.ui.matplotlibwidget.draw()'''


        NbSph=int(self.ui.editNbSpheres.text())
        NbReps=int(self.ui.editNbIter.text())
        H=int(self.ui.editHistBin.text())
        Smin=float(self.ui.editLowLim.text())
        Smax=float(self.ui.editHighLim.text())
        if self.ui.checkBox.isChecked():
            self.hscale='log'
        else:
            self.hscale='lin'
        self.ui.progressBar.setMaximum(NbReps)
        self.ui.progressBar.setValue(0)
        self.A=MCtools.Analyze_1D(q,I,numpy.maximum(0.01*I,E),Nsph=NbSph,Convcrit=1,\
                             Bounds=numpy.array([Smin,Smax]),\
                             Rpfactor=1.5/3,Maxiter=1e5,Histscale=self.hscale,drhosqr=1,Nreps=NbReps,Histbins=H)#feedback=self.updateUI,endf=self.plotBar)
        '''self.c.verbose=False
        self.c.start()'''
        self.plotBar()
    
    def plotBar(self):    
        
        A=self.A
        
        q=A['q']/10
        i=A['Imean']
        error=A['Istd']
        name=self.selectedData+ " mc fit"
        self.parent.data_dict[name]=dataset.dataset(name,q,i, name,parent=[self.selectedData],error=error,type='mc_fit')
        self.parent.redrawTheList()
        self.parent.Replot()        
        #plt.bar(A['Hx'][0:-1],A['Hmean']/sum(A['Hmean']),width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        #plt.show()
        s=A['Hx'][0:-1] #taille
        V=A['Hmean']/sum(A['Hmean'])
        r=(V*3/4.)**(1./3)    #radius from V
        
        n=r/s  #number
        #print n
        #print sum(n)
        self.fig=self.ui.matplotlibwidget.figure
        #x=numpy.arange(100)
        #y=numpy.sin(x)
        self.fig.clear() 
        self.plt=self.fig.add_subplot(211)
        self.plt.set_title('Particule size distribution')
        self.plt.bar(A['Hx'][0:-1],A['Hmean']/sum(A['Hmean']),width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        self.plt.set_xlabel("radium (nm)")
        self.plt.set_ylabel('Volume-weighted')
        if self.ui.checkBox.isChecked():
            self.plt.set_xscale('log')
        self.plt.grid()
        self.plt=self.fig.add_subplot(212) 
        
        self.plt.bar(s,n,width=A['Hwidth'],color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        self.plt.set_xlabel("radium (nm)")
        self.plt.set_ylabel('number')
        if self.ui.checkBox.isChecked():
            self.plt.set_xscale('log')
        self.plt.grid()
        self.fig.tight_layout()
        self.ui.matplotlibwidget.draw()
        
        '''
        self.fig=plt.figure(1)
        #plt.ion()
        plt.subplot(211)
        plt.bar(A['Hx'][0:-1],A['Hmean']/sum(A['Hmean']),width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        plt.xlabel("size (nm)")
        plt.ylabel('Volume-weighted particle size distribution values')
        if self.ui.checkBox.isChecked():
            plt.xscale('log')
        plt.grid()
        plt.subplot(212)
        if self.ui.checkBox.isChecked():
            plt.xscale('log')
        plt.bar(s,n,width=A['Hwidth'],color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        plt.xlabel("size (nm)")
        plt.ylabel('number')
        plt.grid()
        plt.show()'''
        '''
        self.plt2=self.fig2.add_subplot(111) 
        self.plt2.plot(q,i)
        #self.axes.hold(True)
        '''
        #self.ui.matplotlibwidget.draw()
        
        
                    