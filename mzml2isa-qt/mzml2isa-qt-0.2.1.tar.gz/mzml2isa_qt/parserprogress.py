## BACKEND
import sys
import os
import glob
import json
import textwrap
import time

## FRONTEND
from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette

## APP
import mzml2isa.isa
import mzml2isa.mzml

## UI
from mzml2isa_qt.qt.progress import Ui_Dialog as Ui_Progress


class ParserProgressDialog(QDialog):

    def __init__(self, inputDir, outputDir, studyName, userMeta):
        super(ParserProgressDialog, self).__init__()
        self.ui = Ui_Progress()
        self.ui.setupUi(self)

        self.inputDir = inputDir
        self.outputDir = outputDir
        self.studyName = studyName
        self.userMeta = userMeta
      
        if studyName or ('MZML' in [x[-4:].upper() for x in os.listdir(inputDir)]) :
            self.ui.label_study.setText(studyName)
            self.ui.pBar_studies.hide()
            self.parse_thread = ParserThread(inputDir, outputDir, studyName, True, userMeta)

        else:
            self.ui.label_study.hide()
            self.parse_thread = ParserThread(inputDir, outputDir, studyName, False, userMeta)
        
        self.parse_thread.maxFileBar.connect(self.setFilesMaximum)
        self.parse_thread.maxStudyBar.connect(self.setStudiesMaximum)
        self.parse_thread.setFileBar.connect(self.setFilesValue)
        self.parse_thread.setStudyBar.connect(self.setStudiesValue)
        self.parse_thread.LabelStudy.connect(self.setLabelStudy)
        self.parse_thread.Console.connect(self.setParsedFile)
        self.parse_thread.Finish.connect(self.closeProgress)
        self.parse_thread.ErrorSig.connect(self.openErrorDialog)

        self.parse()
    
    def parse(self):
        self.parse_thread.start()   

    def closeEvent(self, event):
        """Closes window when close button is clicked, stopping threads"""
        self.parse_thread.ForceQuitSig.emit()
        self.parse_thread.quit()
        self.reject() 

    def setLabelStudy(self, study):
        self.ui.label_study.setText("Study: " + study)

    def setStudiesMaximum(self, maximum):
        self.ui.pBar_studies.setMaximum(maximum)

    def setStudiesValue(self, value):
        self.ui.pBar_studies.setValue(value)

    def setFilesMaximum(self, maximum):
        self.ui.pBar_parse.setMaximum(maximum)

    def setFilesValue(self, value):
        self.ui.pBar_parse.setValue(value)

    def setParsedFile(self, filename):
        self.ui.textEdit_filename.setText(filename)

    def openErrorDialog(self, message):
        """Opens a popup when an error is encountered"""
        QMessageBox.about(self, 'Error !', message)
        self.reject()

    def closeProgress(self):
        """Closes window when all tasks are finished"""
        if not self.parse_thread.force_quit: QMessageBox.about(self, 'Success !', 'The ISA-Tab files were succesfully created.')
        self.accept()



class ParserThread(QThread):

    maxFileBar = pyqtSignal(int)
    maxStudyBar = pyqtSignal(int)

    setFileBar = pyqtSignal(int)
    setStudyBar = pyqtSignal(int)
    
    LabelStudy = pyqtSignal('QString')
    Console = pyqtSignal('QString') 

    Finish = pyqtSignal()      

    ForceQuitSig = pyqtSignal()

    ErrorSig = pyqtSignal('QString')


    def __init__(self, inputDir, outputDir, studyName, single=True, userMeta = {}):
        super(QThread, self).__init__()
        self.inputDir = inputDir
        self.outputDir = outputDir
        self.studyName = studyName
        self.single = single
        self.userMeta = userMeta

        self.ForceQuitSig.connect(self.forceQuit)

    def __del__(self):
        self.wait()

    def _parseMultipleStudies(self):
        
        # Export studies in input folder
        if self.outputDir == "": 
            self.outputDir = self.inputDir

        # Grabs every directory in input directory
        study_dirs = [d for d in os.listdir(self.inputDir)]# if os.path.isdir(d)]

        # Grabs every directory in input directory containing mzML files
        study_dirs = [d for d in study_dirs if 'MZML' in [ f.split(os.extsep)[-1].upper() for f in os.listdir(os.path.join(self.inputDir, d)) ] ]     
        
        # set maximum
        self.maxStudyBar.emit(len(study_dirs))

        for sindex, study in enumerate(study_dirs):

            # Update progress bar
            self.setStudyBar.emit(sindex)
              
            # Find all mzml files
            mzml_path = os.path.join(os.path.join(self.inputDir, study), "*.mzML")
            mzml_files = [mzML for mzML in glob.glob(mzml_path)]
            mzml_files.sort()

            # Update progress bar
            # self.ui.pBar_parse.setMaximum(len(mzml_files))
            self.maxFileBar.emit(len(mzml_files))
           
            # get meta information for all files
            metalist = []
            for mindex, mzml_file in enumerate(mzml_files):
                # Update progress bar
                self.setFileBar.emit(mindex+1)
                self.Console.emit(os.path.basename(mzml_file))
               
                # Insure the thread will stop if window is closed
                if self.force_quit: 
                    return 0

                # Parse file
                try:
                    metalist.append(mzml2isa.mzml.mzMLmeta(mzml_file).meta_isa)
                except Exception as e:                
                    self.ErrorSig.emit('An error was encountered while parsing {} (study {}):\n\n{}'.format(os.path.basename(mzml_file), 
                                                                                                            study,
                                                                                                            str(type(e).__name__)+" "+str(e),
                                                                                                     )
                                      )
                    self.force_quit = True
                    return 0                

            # Create the isa Tab
            try:
                isa_tab_create = mzml2isa.isa.ISA_Tab(metalist, self.outputDir, study, self.userMeta)
            except Exception as e:
                self.ErrorSig.emit('An error was encountered while writing ISA-Tab (study {}):\n\n{}'.format(study, 
                                                                                                             str(type(e).__name__)+" "+str(e)
                                                                                                       )
                                  )
                self.force_quit = True
                return 0

        return 1


    def _parseSingleStudy(self):
        
        # Export in input study folder
        if self.outputDir == "": # Case were studies are saved in input directory
            self.outputDir = os.path.dirname(self.inputDir)
            self.studyName = os.path.basename(self.inputDir)

        self.LabelStudy.emit(self.studyName)

        # Find all mzml files
        mzml_path = os.path.join(self.inputDir, "*.mzML")
        mzml_files = [mzML for mzML in glob.glob(mzml_path)]
        mzml_files.sort()

        # Update progress bar
        self.maxFileBar.emit(len(mzml_files))

        # get meta information for all files
        metalist = []
        for index, mzml_file in enumerate(mzml_files):
            # Update progress bar
            self.setFileBar.emit(index+1)
            self.Console.emit("> Parsing " + os.path.basename(mzml_file))

            # Insure the thread will stop if window is closed
            if self.force_quit: 
                return 0

            # Parse file
            try:
                metalist.append(mzml2isa.mzml.mzMLmeta(mzml_file).meta_isa)                
            except Exception as e:                
                self.ErrorSig.emit('An error was encountered while parsing {}:\n\n{}'.format(os.path.basename(mzml_file), 
                                                                                             str(type(e).__name__)+" "+str(e)
                                                                                             )
                                  )
                self.force_quit = True
                return 0


        # Create the isa Tab
        self.Console.emit("> Creating ISA-Tab files")
        try:
            isa_tab_create = mzml2isa.isa.ISA_Tab(metalist, self.outputDir, self.studyName, self.userMeta)
        except Exception as e:
            self.ErrorSig.emit('An error was encountered while writing ISA-Tab in {}:\n\n{}'.format(self.outputDir, 
                                                                                                    str(type(e).__name__)+" "+str(e)
                                                                                                   )
                              )
            return 0
            


        # Return Accepted if no errors were encountered
        return 1
        

    def run(self):
        time.sleep(1)
        self.force_quit = False
        if self.single:
            self._parseSingleStudy()
        else:
            self._parseMultipleStudies()
        # Close finish window
        self.Finish.emit()

    def forceQuit(self):
        self.force_quit = True
