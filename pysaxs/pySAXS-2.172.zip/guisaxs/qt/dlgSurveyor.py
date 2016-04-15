from PyQt4 import QtGui, QtCore
from PyQt4.Qt import QString
from fileinput import filename
from guidata.dataset.qtitemwidgets import QStringList
from pyFAI import azimuthalIntegrator
from pySAXS.guisaxs import dataset
from pySAXS.guisaxs.qt import dlgSurveyorui
from pySAXS.guisaxs.qt import preferences
from pySAXS.guisaxs.qt import QtMatplotlib
from pySAXS.tools import FAIsaxs
from pySAXS.tools import filetools
from reportlab.graphics.widgets.table import TableWidget
from spyderlib.widgets.externalshell import namespacebrowser
from time import sleep
import fabio
import numpy
import os.path, dircache
import pyFAI
import sys
import threading
import time
import pySAXS

class SurveyorDialog(QtGui.QMainWindow):
    def __init__(self, parent=None, parameterfile=None, outputdir=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = dlgSurveyorui.Ui_surveyorDialog()
        self.setWindowTitle('Continuous Radial averaging tool for pySAXS')
        if parent is not None:
            # print "icon"
            self.setWindowIcon(parent.windowIcon())
        
        self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.paramFileButton, QtCore.SIGNAL("clicked()"), self.OnClickparamFileButton)
        QtCore.QObject.connect(self.ui.changeDirButton, QtCore.SIGNAL("clicked()"), self.OnClickchangeDirButton)
        QtCore.QObject.connect(self.ui.STARTButton, QtCore.SIGNAL("clicked()"), self.OnClickSTARTButton)
        QtCore.QObject.connect(self.ui.STOPButton, QtCore.SIGNAL("clicked()"), self.OnClickSTOPButton)
        QtCore.QObject.connect(self.ui.plotChkBox, QtCore.SIGNAL("clicked()"), self.OnClickPlotCheckBox)
        self.ui.progressBar.setValue(0)
        self.ui.STARTButton.setEnabled(True)
        self.ui.STOPButton.setDisabled(True)
        
        self.parent = parent
        self.workingdirectory = None
        self.parameterfile=parameterfile
        if self.parameterfile is not None:
            self.ui.paramTxt.setText(str(parameterfile))
            
         #-- get preferences
        self.pref=preferences.prefs()
        
        if parent is not None:
            self.printout = parent.printTXT
            self.workingdirectory = parent.workingdirectory
        else :
            self.workingdirectory = ""
            
            if self.pref.fileExist():
                self.pref.read()
                #print "file exist"
                dr=self.pref.get('defaultdirectory')
                if dr is not None:
                    self.workingdirectory=dr
                    #print 'set wd',dr
                    self.ui.DirTxt.setText(self.workingdirectory)
                pf=self.pref.get('parameterfile',section="pyFAI")
                if pf is not None:
                    self.parameterfile=pf
                    self.ui.paramTxt.setText(self.parameterfile)
            else:
                self.pref.save()
        self.imageToolWindow = None
        self.updateListInit()
    def OnClickparamFileButton(self):
        '''
        Allow to select a parameter file
        '''
        fd = QtGui.QFileDialog(self)
        filename = fd.getOpenFileName(directory=self.workingdirectory)
        self.workingdirectory = filename
        # print filename
        self.ui.paramTxt.setText(filename)
        # self.ui.editor_window.setText(plik)

    def OnClickSTARTButton(self):
        '''
        Used when start button is clicked
        '''
        print "start"
        self.radialPrepare()
        self.ui.progressBar.setValue(100)
        self.ui.STOPButton.setEnabled(True)
        self.ui.STARTButton.setDisabled(True)
        if self.ui.refreshTimeTxt.text() == '':
            time = 30
        else :
            time = float(self.ui.refreshTimeTxt.text())    
        print(time)
        self.t = Intervallometre(time, self.updateList(), self)
        self.t.start()
        
    def OnClickSTOPButton(self):
        '''
        Used when stop button is clicked
        '''
        print "stop"
        self.ui.progressBar.setValue(0)
        self.ui.STARTButton.setEnabled(True)
        self.ui.STOPButton.setDisabled(True)
        self.t.stop()
    def OnClickchangeDirButton(self):
        '''
        Allow to select a directory
        '''
        fd = QtGui.QFileDialog(self, directory=self.workingdirectory)
        fd.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        if fd.exec_() == 1:
            dir = str(fd.selectedFiles().first())
            # dir=fd.getOpenFileName()
            self.ui.DirTxt.setText(dir)
            self.workingdirectory = dir
            self.updateListInit()
            self.pref.set('defaultdirectory', self.workingdirectory)
            self.pref.save()
            
    def updateList(self):
        '''
        Update the list
        '''
        print '-'
        self.ext = str(self.ui.extensionTxt.text())
        if self.ext == '':
              self.ext = '*.*'
        self.fp = str(self.ui.DirTxt.text())
        listoffile = self.getList(self.fp, self.ext)
        print listoffile
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.setRowCount(len(listoffile))
        headerNames = ["File", "date", "processed", "new"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
        self.ui.tableWidget.setColumnWidth(0, 220)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 70)
        self.ui.tableWidget.setColumnWidth(3,50)
        i = 0
        for name in listoffile:
            self.ui.tableWidget.setItem(i, 0, QtGui.QTableWidgetItem(name))
            self.ui.tableWidget.setItem(i, 1, QtGui.QTableWidgetItem(str(listoffile[name][0])))
            self.ui.tableWidget.setItem(i, 2, QtGui.QTableWidgetItem(str(listoffile[name][1])))
            self.ui.tableWidget.setItem(i, 3, QtGui.QTableWidgetItem(str(listoffile[name][2])))
            self.ui.tableWidget.setRowHeight(i, 20)
            if not listoffile[name][1] :
                try :
                    self.radialAverage(self.fp + "\\" + name)
                except:
                    print "error file"
                
            i += 1
      #  self.timer()
        self.listoffileVerif = filetools.listFiles(self.fp,self.ext)
        self.listoffileVerif = listoffile

    def updateListInit(self):
        '''
        Update the initial List WITHOUT treatment 
        '''
        print '-'
        self.ext = str(self.ui.extensionTxt.text())
        if self.ext == '':
              self.ext = '*.*'
        self.fp = str(self.ui.DirTxt.text())
        listoffile = self.getList(self.fp, self.ext)
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.setRowCount(len(listoffile))
        headerNames = ["File", "date", "processed", "new"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
        self.ui.tableWidget.setColumnWidth(0, 220)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 70)
        self.ui.tableWidget.setColumnWidth(3,50)  
        i = 0
        for name in listoffile:
            self.ui.tableWidget.setItem(i, 0, QtGui.QTableWidgetItem(name))
            self.ui.tableWidget.setItem(i, 1, QtGui.QTableWidgetItem(str(listoffile[name][0])))
            self.ui.tableWidget.setItem(i, 2, QtGui.QTableWidgetItem(str(listoffile[name][1])))
            self.ui.tableWidget.setItem(i, 3, QtGui.QTableWidgetItem(str(listoffile[name][2])))
            self.ui.tableWidget.setRowHeight(i, 20)          
            i += 1
        self.listoffileVerif = filetools.listFiles(self.fp,self.ext)
        self.listoffileVerif = listoffile
    
    def getList(self, fp, ext):
        listoffile = filetools.listFiles(self.fp, self.ext)
        files = {}
        for name in listoffile:
            fich = filetools.getFilename(name)
            dt = filetools.getModifiedDate(name)
            newfn = filetools.getFilenameOnly(name)
            ficTiff = newfn
            newfn += '.rgr'
            # print newfn
            if filetools.fileExist(newfn) :
                proc = True
                new = False
            else:              
                proc = False
                new = True
            files[fich] = [dt, proc, new]    
        return files
    
    def printTXT(self, txt="", par=""):
        '''
        for printing messages
        '''
        if self.printout == None:
            print(str(txt) + str(par))
        else:
            self.printout(txt, par)

    def radialPrepare(self):
        self.fai = FAIsaxs.FAIsaxs()
        filename = self.ui.paramTxt.text()
        if not os.path.exists(filename):
            self.printTXT(filename + ' does not exist')
            return
        outputdir = self.ui.DirTxt.text()
        self.fai.setGeometry(filename)
        self.qDiv = self.fai.getProperty('user.qDiv')
        if self.qDiv is None:
            self.qDiv = 1000
        self.mad = self.fai.getIJMask()
        maskfilename = self.fai.getMaskFilename()
  
    def radialAverage(self, imageFilename):
        t0=time.time()
        im = fabio.open(imageFilename)
        newname = filetools.getFilenameOnly(imageFilename) + ".rgr"
        qtemp, itemp, stemp = self.fai.integrate1d(im.data, self.qDiv, filename=newname, mask=self.mad, error_model="poisson")
        print time.time()-t0, " s"
        try:
            q = qtemp[numpy.nonzero(itemp)]
            i = itemp[numpy.nonzero(itemp)]
            s = stemp[numpy.nonzero(itemp)]
            self.plotapp.addData(q, i, label=imageFilename)#,error=s)
            self.plotapp.replot()
            print "message"
        except:
            print "Error plot"
        self.fai.saveGeometry(imageFilename)#save rpt
        
    def OnClickPlotCheckBox(self):
        if self.ui.plotChkBox.isChecked():
            self.plotapp=QtMatplotlib.QtMatplotlib()
            self.plotapp.show()
        else:
            self.plotapp.close()
class Intervallometre(threading.Thread):
 
    def __init__(self, duree, fonction, parent):
        threading.Thread.__init__(self)
        self.duree = duree
        self.fonction = fonction
        self.parent = parent
        self.encore = True
    def run(self):
        while self.encore:
            self.parent.updateList()
            sleep(self.duree)
 
    def stop(self):
        self.encore = False
        
if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = SurveyorDialog()
  myapp.show()
  sys.exit(app.exec_())
  
