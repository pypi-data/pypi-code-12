'''
--------------------------------------------------------------------------
Copyright (C) 2016 Lukasz Laba <lukaszlab@o2.pl>

File version 0.3 date 2016-06-02

This file is part of SeePy.
SeePy is a python script visualisation tool.
http://seepy.org/

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
'''

import sys
import os
import subprocess
import traceback
import idlelib

from PyQt4 import QtCore, QtGui
import mistune
from Tkinter import Tk
from tkFileDialog import askopenfilename
from tkSimpleDialog import askstring
import easygui

from Code import Code
from Shell import Shell

_appname = 'SeePy'
_version = '0.2.1 (beta)'

class Main(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self, None)
        self.initUI()

    def initUI(self):
        # -- Main Toolbar --
        newAction = QtGui.QAction(QtGui.QIcon("icons/new.png"),"New",self)
        newAction.setShortcut("Ctrl+N")
        newAction.setStatusTip("Create new *.py script from template and set it as watched")
        newAction.triggered.connect(self.New)

        openAction = QtGui.QAction(QtGui.QIcon("icons/open.png"),"Open",self)
        openAction.setStatusTip("Open existing *.py script and set it as watched")
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.Open)

        savecopyAction = QtGui.QAction(QtGui.QIcon("icons/saveas.png"),"Save copy as",self)
        savecopyAction.setStatusTip("Save current script copy as same name and set it as watched")
        savecopyAction.setShortcut("Ctrl+s")
        savecopyAction.triggered.connect(self.SaveCopy)

        reloadAction = QtGui.QAction(QtGui.QIcon("icons/reload.png"),"Reload",self)
        reloadAction.setStatusTip("Reload watched *.py script")
        reloadAction.setShortcut("F5")
        reloadAction.triggered.connect(self.Reload)

        editAction = QtGui.QAction(QtGui.QIcon("icons/edit.png"),"Edit",self)
        editAction.setStatusTip("It opens to edit current *.py script in standart Python IDLE")
        editAction.setShortcut("Ctrl+E")
        editAction.triggered.connect(self.Edit)

        showhtmlAction = QtGui.QAction(QtGui.QIcon("icons/html.png"),"Show report as HTML",self)
        showhtmlAction.setStatusTip("It shows report as HTML code")
        showhtmlAction.triggered.connect(self.ShowHTML)

        showmarkdownAction = QtGui.QAction(QtGui.QIcon("icons/markdown.png"),"Show report as Markdown",self)
        showmarkdownAction.setStatusTip("It shows report as Markdown code")
        showmarkdownAction.triggered.connect(self.ShowMarkdown)

        previewmarkdownAction = QtGui.QAction(QtGui.QIcon("icons/previewmarkdown.png"),"Preview some Markdown",self)
        previewmarkdownAction.setStatusTip("You can preview some Markdown document - it not change watched *.py script")
        previewmarkdownAction.triggered.connect(self.PreviewMarkdown)

        savemarkdownAction = QtGui.QAction(QtGui.QIcon("icons/savemarkdown.png"),"Save report as Markdown file",self)
        savemarkdownAction.setStatusTip("Save report as Markdown file")
        savemarkdownAction.triggered.connect(self.SaveMarkdown)

        printAction = QtGui.QAction(QtGui.QIcon("icons/print.png"),"Print document",self)
        printAction.setStatusTip("Print document")
        printAction.setShortcut("Ctrl+P")
        printAction.triggered.connect(self.Print)

        helpAction = QtGui.QAction(QtGui.QIcon("icons/help.png"),"Help",self)
        helpAction.setStatusTip("Help information")
        helpAction.setShortcut("F1")
        helpAction.triggered.connect(self.Help)

        aboutAction = QtGui.QAction(QtGui.QIcon("icons/about.png"),"About SeePy",self)
        aboutAction.setStatusTip("SeePy project information")
        aboutAction.triggered.connect(self.About)

        tutorialAction = QtGui.QAction(QtGui.QIcon("icons/tutorial.png"),"Tutorial",self)
        tutorialAction.setStatusTip("Open tutorial script")
        tutorialAction.triggered.connect(self.Tutorial)

        syntaxAction = QtGui.QAction(QtGui.QIcon("icons/syntax.png"),"Syntax help",self)
        syntaxAction.setStatusTip("Show SeePy syntax help")
        syntaxAction.setShortcut("F2")
        syntaxAction.triggered.connect(self.Syntax)
        
        floatprecisionAction = QtGui.QAction(QtGui.QIcon(" "),"Float precision",self)
        floatprecisionAction.setStatusTip("Set float display precision")
        floatprecisionAction.triggered.connect(self.Floatprecision)

        self.toolbar = self.addToolBar("Main")
        self.toolbar.addAction(newAction)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(savecopyAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(reloadAction)
        self.toolbar.addAction(editAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(printAction)
        self.toolbar.addAction(savemarkdownAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(showhtmlAction)
        self.toolbar.addAction(showmarkdownAction)
        self.toolbar.addAction(previewmarkdownAction)
        self.toolbar.addSeparator()
        self.toolbar.addAction(aboutAction)
        self.toolbar.addAction(helpAction)
        self.toolbar.addAction(syntaxAction)
        self.toolbar.addAction(tutorialAction)
        self.toolbar.addSeparator()
        #languages = QtGui.QComboBox(self)
        #languages.setEditable(True)
        #languages.setMinimumContentsLength(3)
        #languages.addItem(str('no language detected'))
        #self.toolbar.addWidget(languages)

        # -- Text Browser --
        self.textBrowser = QtGui.QTextBrowser(self)
        self.setCentralWidget(self.textBrowser)
        self.textBrowser.anchorClicked.connect(self.on_anchor_clicked)

        # -- Statusbar --
        self.status = self.statusBar()

        # --Window settings --
        self.setGeometry(100, 100, 720, 700)
        #self.setWindowTitle(self.appName)
        self.setWindowIcon(QtGui.QIcon("icons/logo.png"))
        self.show()

        # -- Menubar --
        menubar = self.menuBar()
        #---
        file = menubar.addMenu("File")
        file.addAction(newAction)
        file.addAction(openAction)
        file.addAction(printAction)
        #---
        export = menubar.addMenu("Script")
        export.addAction(reloadAction)
        export.addAction(editAction)
        export.addAction(showhtmlAction)
        export.addAction(showmarkdownAction)
        export.addAction(showmarkdownAction)
        export.addAction(floatprecisionAction)
        #---
        info = menubar.addMenu("Info")
        info.addAction(aboutAction)
        info.addAction(helpAction)
        info.addAction(syntaxAction)
        info.addAction(tutorialAction)
        
    def closeEvent(self, event):
        Environment.delete_tmpfile() #Cleaning SeePy tmp files
        event.accept()

    def New(self):
        ScriptCode.newFile('x_newtemplate.py', 'Save new script as', 'newScript.py')
        setWatcher()
        AppReload()

    def Open(self):
        if ScriptCode.script_path:
            Environment.delete_tmpfile() #Cleaning SeePy tmp files
        ScriptCode.openFile()
        setWatcher()
        AppReload()

    def SaveCopy(self):
        if ScriptCode.script_path :
            newName = 'Copy_' + os.path.basename(ScriptCode.script_path)
            ScriptCode.newFile(ScriptCode.script_path, 'Save copy script as', newName)
            setWatcher()
            AppReload()
        else:
            easygui.msgbox('Please create or open script first', 'Info')

    def Reload(self):
        if ScriptCode.script_path :
            AppReload()
        else:
            easygui.msgbox('Please create or open script first', 'Info')

    def Edit(self):
        if ScriptCode.script_path :
            IDLEpath = vars(idlelib)['__path__'][0] + '/idle.pyw'
            subprocess.Popen(['python', IDLEpath, ScriptCode.script_path])
        else:
            easygui.msgbox('Please create or open script first', 'Info')

    def ShowHTML(self):
        if ScriptCode.script_path :
            show_somecode(Environment.report_html)
        else:
            easygui.msgbox('Please create or open script first', 'Info')

    def ShowMarkdown(self):
        if ScriptCode.script_path :
            show_somecode(Environment.report_markdown)
        else:
            easygui.msgbox('Please create or open script first', 'Info')

    def PreviewMarkdown(self):
        root = Tk()
        root.withdraw()
        filename = askopenfilename( parent=root,
                                    title='Open Marktdown document', 
                                    filetypes=[('Markdown document', '*.md')], 
                                    initialdir=ScriptCode.savedir   )
        root.destroy()
        show_markdown(open(filename, 'r').read())

    def SaveMarkdown(self):
        if ScriptCode.script_path :
            initname = os.path.basename(ScriptCode.script_path).replace('.py', '.md')
            Environment.save_report_markdown(ScriptCode.savedir, initname)
        else:
            easygui.msgbox('Please create or open script first', 'Info')

    def Print(self):
        dialog = QtGui.QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.textBrowser.document().print_(dialog.printer())

    def Help(self):
        show_markdown(open('x_help.md', 'r').read())

    def About(self):
        show_markdown(open('x_about.md', 'r').read())

    def Tutorial(self):
        ScriptCode.newFile('x_tutorial.py', 'Pleas save your copy of tutorial as', 'myTutorial.py')
        setWatcher()
        AppReload()
        self.Edit()

    def Syntax(self):
        show_markdown(open('x_syntax.md', 'r').read())
        
    def Floatprecision(self):
        if ScriptCode.script_path :
            root = Tk()
            root.withdraw()
            value = askstring(  parent=root, 
                                title='Float display precysion',
                                prompt='Set precioson',
                                initialvalue=Environment.float_display_precison ) 
            root.destroy()
            Environment.float_display_precison = int(value)
            AppReload()
        else:
            easygui.msgbox('Please create or open script first', 'Info')
        
    def on_anchor_clicked(self,url):
        id = str(url.toString())
        scrol_value = myapp.textBrowser.verticalScrollBar().value()
        self.textBrowser.setSource(QtCore.QUrl())
        myapp.textBrowser.verticalScrollBar().setValue(scrol_value)
        ScriptCode.editCode(id)

def AppReload ():
    try:
        ScriptCode.parse()
        Environment.run_parsed()
        #---
        scrol_value = myapp.textBrowser.verticalScrollBar().value()
        #---
        myapp.textBrowser.clear()
        myapp.textBrowser.setHtml(Environment.report_html)
        myapp.textBrowser.reload()
        #---
        myapp.textBrowser.verticalScrollBar().setValue(scrol_value)
    except Exception as e: 
        easygui.msgbox(str(traceback.format_exc()), 'Some problem - ' + str(e))
    #---
    myapp.setWindowTitle(_appname + ' ' + _version + ' - ' + os.path.basename(ScriptCode.script_path))

@QtCore.pyqtSlot(str)
def script_changed(path):
    AppReload()

def setWatcher():
    global fs_watcher
    fs_watcher = None
    fs_watcher = QtCore.QFileSystemWatcher([ScriptCode.script_path])
    fs_watcher.connect(fs_watcher, QtCore.SIGNAL('fileChanged(QString)'), script_changed)

def preview_somescript(path):
    ScriptCode.parse(path)
    Environment.run_parsed()
    myapp.textBrowser.setHtml(Environment.report_html)

def show_somecode(code):
    code = "````\n" + code + "\n````"
    code_html = mistune.markdown(code)
    myapp.textBrowser.setHtml(code_html)

def show_markdown(markdown):
    code_html = mistune.markdown(markdown)
    myapp.textBrowser.setHtml(code_html)

if __name__ == "__main__":
    #--PyQt objects
    app = QtGui.QApplication(sys.argv)
    myapp = Main()
    #----
    ScriptCode = Code()
    Environment = Shell()
    #---assigning code to shell
    Environment.assign_code(ScriptCode)
    #---
    myapp.setWindowTitle(_appname + ' ' + _version)
    show_markdown(open('x_startpage.md', 'r').read())
    #----Tests
    #ScriptCode.parse('test.py')
    #show_somecode(ScriptCode.code_parsed)
    #Environment.run_parsed()
    #myapp.textBrowser.setHtml(Environment.report_html)
    #preview_somescript('test.py')
    #----
    myapp.show()
    sys.exit(app.exec_())