'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.1

This file is part of SeePy.
SeePy is a structural engineering design Python package.
http://struthon.org/

SeePy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

SeePy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
File version 0.x changes:
- xxxxxx
'''

import sys
import os

import easygui

from PyQt4 import QtCore, QtGui

from Code import Code
from Shell import Shell

import subprocess
        
import idlelib

class Main(QtGui.QMainWindow):
 
    def __init__(self):
        QtGui.QMainWindow.__init__(self,None)
        self.appName = 'SeePy'
        self.initUI()

    def initUI(self):
        #-- Upper Toolbar -- 
        newAction = QtGui.QAction(QtGui.QIcon("icons/new.png"),"New",self)
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip("Create a new *.py document")
        newAction.triggered.connect(self.New)
        
        openAction = QtGui.QAction(QtGui.QIcon("icons/open.png"),"Open",self)
        openAction.setStatusTip("Open existing document")
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.Open)
 
        reloadAction = QtGui.QAction(QtGui.QIcon("icons/reload.png"),"Reload",self)
        reloadAction.setStatusTip("Reload watched *.py script")
        reloadAction.setShortcut("Ctrl+E")
        reloadAction.triggered.connect(self.Reload)

        editAction = QtGui.QAction(QtGui.QIcon("icons/edit.png"),"Edit",self)
        editAction.setStatusTip("Edit watched *.py script")
        editAction.setShortcut("Ctrl+G")
        editAction.triggered.connect(self.Edit)
        
        exportAction = QtGui.QAction(QtGui.QIcon("icons/export.png"),"Export",self)
        exportAction.setStatusTip("Export to..")
        exportAction.setShortcut("Ctrl+H")
        exportAction.triggered.connect(self.Export)
 
 
        self.toolbar = self.addToolBar("Options")
        self.toolbar.addAction(newAction)
        self.toolbar.addAction(openAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(reloadAction)
        self.toolbar.addAction(editAction)
        self.toolbar.addAction(exportAction)
        self.addToolBarBreak()
         
        #------- Text Browser -----------------------------------
        self.textBrowser = QtGui.QTextBrowser(self)
        self.setCentralWidget(self.textBrowser)

        #------- Statusbar ------------------------------------
        self.status = self.statusBar()
 
        #---------Window settings --------------------------------
        self.setGeometry(100,100,700,700)
        self.setWindowTitle(self.appName)
        self.setWindowIcon(QtGui.QIcon("icons/logo.png"))
        
        self.show()
 
        #------- Menubar --------------------------------------
        menubar = self.menuBar()
        #---
        file = menubar.addMenu("File")
        file.addAction(newAction)
        file.addAction(openAction)
        file.addAction(editAction)
        #---        
        export = menubar.addMenu("Export")
        export.addAction(exportAction)
        #---
        help = menubar.addMenu("Help")
        help.addAction(exportAction)

    #-------- Toolbar slots -----------------------------------
    def New(self):
        ScriptCode.newFile()
        self.Reload()
        
    def Open(self):
        ScriptCode.openFile()
        self.Reload()

    def Reload(self):
        ScriptCode.parse()
        Environment.run_parsed(ScriptCode)
        #---
        myapp.textBrowser.setHtml(Environment.report_html)
        #---
        self.setWindowTitle(self.appName + ' - ' + os.path.basename(ScriptCode.script_path))
        
    def Edit(self):
        if ScriptCode.script_path :
            IDLEpath = vars(idlelib)['__path__'][0] + '/idle.pyw'
            subprocess.Popen(['python', IDLEpath, ScriptCode.script_path])
        else:
            easygui.msgbox('Please create or open script first', 'Info')
        
    def Export(self):
        print 'Export'

#-----------------------------------------------------
#-----------------------------------------------------
'''!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
def action_New():
   pass
                
def update_raport():
    ScriptCode.parse()
    Environment.run_parsed(ScriptCode)
    myapp.textBrowser.setHtml(Environment.report_html)
'''

if __name__ == "__main__":
    #----PyQt objects
    app = QtGui.QApplication(sys.argv)
    myapp = Main()
    #----
    ScriptCode = Code()
    Environment = Shell()
    #----
    myapp.show()
    sys.exit(app.exec_())
    
#-----------------------Tmp Notatki-------------------------------------------    
#File wach
#http://stackoverflow.com/questions/182197/how-do-i-watch-a-file-for-changes-using-python

    
'''
           skrypt_org ->/zmiana skladni/ -> skrypt_zmieniony-> / uruchomienie z funkcjami commmnt/ -> markdown -> HTML ->GUI
MAIN      +++++++++++                                                                                             ++++++++++
Parser                   ++++++++++++++++++++++++++++++++++++
Envir                                                           ++++++++++++++++++++++++++++++++++++++++++++++++



from PyQt4 import QtCore

@QtCore.pyqtSlot(str)
def directory_changed(path):
    print('Directory Changed!!!')

@QtCore.pyqtSlot(str)
def file_changed(path):
    print('File Changed!!!')

fs_watcher = QtCore.QFileSystemWatcher(['/path/to/files_1', '/path/to/files_2', '/path/to/files_3'])

fs_watcher.connect(fs_watcher, QtCore.SIGNAL('directoryChanged(QString)'), directory_changed)
fs_watcher.connect(fs_watcher, QtCore.SIGNAL('fileChanged(QString)'), file_changed)


    def on_anchor_clicked(self,url):
        text = str(url.toString())
        print text
        self.ui.textBrowser.setSource(QtCore.QUrl()) #stops the page from changing
        if text.startswith('some_special_identifier://'):
            #self.ui.textBrowser.setSource(QtCore.QUrl()) #stops the page from changing
            function = text.replace('some_special_identifier://','')
            print function 
            if hasattr(self,function):
                getattr(self,function)()

'''
    
    
    
