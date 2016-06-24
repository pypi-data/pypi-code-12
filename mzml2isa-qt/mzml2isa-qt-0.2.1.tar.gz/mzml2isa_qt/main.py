#!/usr/bin/env python3

## BACKEND
import sys
import os
import glob
import json
import textwrap
import time

## APP
import mzml2isa.isa
import mzml2isa.mzml

## FRONTEND
from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette

## UI
from mzml2isa_qt.qt.main import Ui_MainWindow

## UI MODULES
from mzml2isa_qt.usermeta import UserMetaDialog
from mzml2isa_qt.parserprogress import ParserProgressDialog



class MainWindow(QMainWindow):
 

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect up the buttons.
        self.ui.PushBut_convert.clicked.connect(self.launchParser)
        self.ui.toolButton_input_explore.clicked.connect(self.exploreInput)
        self.ui.toolButton_output_explore.clicked.connect(self.exploreOutput)
        self.ui.toolButton_metadata.clicked.connect(self.getUserMeta)

        # Connect up the checkboxes
        self.ui.cBox_multiple.stateChanged.connect(self.toggleMultiple)
        self.ui.cBox_export.stateChanged.connect(self.toggleExport)

        # init some attributes
        self.userMeta = {}

    def toggleMultiple(self, int):
        """ Toggle the Study LineEdit when multiple studies checkbox is checked """
        if self.ui.cBox_multiple.isChecked():
            self.ui.lineEdit_study.setEnabled(False)
            self.ui.lineEdit_study.setText("")
            self.ui.lbl_study_error.setText("")
        else:
            if not self.ui.cBox_export.isChecked():
                self.ui.lineEdit_study.setEnabled(True)

    def toggleExport(self, int):
        """ Toggle the Study LineEdit when export studies checkbox is checked """
        if self.ui.cBox_export.isChecked():

            self.ui.lineEdit_output.setEnabled(False)
            self.ui.lineEdit_output.setText("")
            self.ui.lbl_output_error.setText("")
            self.ui.toolButton_output_explore.setEnabled(False)
 
            self.ui.lineEdit_study.setEnabled(False)
            self.ui.lineEdit_study.setText("")
            self.ui.lbl_study_error.setText("")

        else:
            self.ui.lineEdit_output.setEnabled(True)
            self.ui.toolButton_output_explore.setEnabled(True)
            if not self.ui.cBox_multiple.isChecked():
                self.ui.lineEdit_study.setEnabled(True)
            
    def launchParser(self):
        """Checks if arguments are ok, then launches the parser window"""

        LEGIT, inputDir, outputDir, studyName = self.checkArgs()
        if not LEGIT: return
                
        # Open the progress window
        self.progress = ParserProgressDialog(inputDir, outputDir, studyName, self.userMeta)
        self.progress.exec_()

        # Resets field after parser was launched
        self.ui.lineEdit_input.setText("")
        self.ui.lineEdit_output.setText("")
        self.ui.lineEdit_study.setText("")

    def exploreInput(self):
        """Open file explorer and fills the input field"""
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.lineEdit_input.setText(directory)  

    def exploreOutput(self):
        """Open file explorer and fills the output field"""
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.ui.lineEdit_output.setText(directory)  
        
    def checkArgs(self):
        """Check for arguments and displays errors if any"""
        inputDir = os.path.expanduser(self.ui.lineEdit_input.text())
        outputDir = os.path.expanduser(self.ui.lineEdit_output.text())
        studyName = self.ui.lineEdit_study.text()
        LEGIT = True

        # inputDir errors checking
        if not inputDir:
            self.ui.lbl_input_error.setText("Please provide a directory")
            LEGIT = False
        elif not os.path.isdir(inputDir):
            self.ui.lbl_input_error.setText("Directory does not exist")
            LEGIT = False
        elif not os.access(inputDir, os.R_OK):
            self.ui.lbl_input_error.setText("Directory has no read permissions")
            LEGIT = False
        elif not self.ui.cBox_multiple.isChecked(): 
            # list mzML files in study folder
            if not [x for x in os.listdir(inputDir) if x[-4:].upper() == "MZML"]:   
                self.ui.lbl_input_error.setText("Directory contains no mzML files")
                LEGIT = False
            else:
                self.ui.lbl_input_error.setText("")    
        elif self.ui.cBox_export.isChecked() and not os.access(inputDir, os.W_OK):
            self.ui.lbl_input_error.setText("Directory has no write permissions")
            LEGIT = False
        else:
            self.ui.lbl_input_error.setText("")

        # OutputDir errors checking
        if self.ui.lineEdit_output.isEnabled():
            if not outputDir:
                self.ui.lbl_output_error.setText("Please provide a directory")
                LEGIT = False
            elif not os.path.isdir(outputDir):
                self.ui.lbl_output_error.setText("Directory does not exist")
                LEGIT = False
            elif not os.access(outputDir, os.W_OK):
                self.ui.lbl_output_error.setText("Directory has no write permissions")
                LEGIT = False
            else:
                self.ui.lbl_output_error.setText("")
        else:
            self.ui.lbl_output_error.setText("")

        # StudyName errors checking
        if self.ui.lineEdit_study.isEnabled() and not studyName:	
            self.ui.lbl_study_error.setText("Please provide a study name")
            LEGIT = False
        else:
            self.ui.lbl_study_error.setText("")

        return LEGIT, inputDir, outputDir, studyName

    def getUserMeta(self):
        if not hasattr(self, 'userMeta'):
            self.userMeta = {}
        self.userMetaDialog = UserMetaDialog(self, self.userMeta)
        self.userMetaDialog.SigUpdateMetadata.connect(self.updateMetadata)
        self.userMetaDialog.exec_()

    def updateMetadata(self, json_metadata):
        self.userMeta = json.loads(json_metadata)


def main():
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == '__main__':   
    main()
