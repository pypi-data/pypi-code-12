#!/usr/bin/env python3

## BACKEND
import sys
import os
import json

## FRONTEND
from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QStandardItemModel, QStandardItem

## UI
from mzml2isa_qt.qt.ols import Ui_Dialog as Ui_Ols

## UI MODULES
from mzml2isa_qt.scrapers import OlsOntologist, OlsSearcher, OlsExplorer



class OlsDialog(QDialog):
    """Dialog to search the OLS for an ontology

    The OlsDialog uses threads to connect to the Ontology Lookup Service,
    and search for a query, get results, and get informations about 
    ontologies. 

    Selected ontology is returned as a json serialized dict.
    """

    SigSearchCompleted = pyqtSignal('QString')

    def __init__(self, parent=None, allow_onto=False):
        super(OlsDialog, self).__init__(parent)

        self.ui = Ui_Ols()
        self.ui.setupUi(self)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

        self.onto = {}
        self.ontothreads = {}
        self.allow_onto = allow_onto
        self.entry = None

        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.ui.searchButton.clicked.connect(self.search)
        self.ui.queryLine.setFocus()

    def search(self):
        """Launch the OlsSearchThread"""
        self.searcher = OlsSearcher(self.ui.queryLine.text())
        self.searcher.Finished.connect(self.updateSearchResults)
        self.searcher.start()

    def updateSearchResults(self, jresults):
        """Update TreeView with search results."""

        self.model = QStandardItemModel()
        self.orderedResults = {}

        if jresults:
            
            self.results = json.loads(jresults)

            for result in self.results:
                prefix = result['ontology_prefix']
                
                # Create a new node & append it to StandardItemModel
                # if the ontology of the result is not already in StandardItemModel
                if not self.model.findItems(prefix):
                    node = QStandardItem(prefix)
                    self.model.appendRow(node)
                    
                # Look for details of that new ontology if that ontology is not
                # already memo table and not other OlsOntologist is querying
                # informations about that ontology
                if prefix not in self.ontothreads and prefix not in self.onto:
                    thread = OlsOntologist(prefix)
                    thread.Finished.connect(self._memo_onto)
                    thread.start()
                    self.ontothreads[prefix] = thread

                # Add the entry to its ontology node
                result['tag'] = result['short_form'].replace('_', ':') + ' - ' + result['label']    
                self.model.findItems(prefix)[0].appendRow(
                        QStandardItem(result['tag'])
                    )

        self.model.sort(0)
        self.ui.ontoTree.setModel(self.model)
        #self.ui.ontoTree.expandAll()
        self.model.setHorizontalHeaderLabels(["Object"])
        self.ui.ontoTree.selectionModel().selectionChanged.connect(
            lambda selection: self.updateInterface(selection.indexes()[0])
            )
        self.ui.ontoTree.clicked.connect(self.updateInterface)
        self.ui.ontoTree.doubleClicked.connect(self.onDoubleClick)
        
    def _getResultFromIndex(self, index):
        """Iterate on self.results to get the right entry"""
        crawler = self.model.itemFromIndex(index)
        self.entry = None
        for x in self.results:
            if x['tag'] == crawler.text():
                self.entry = x 
        return crawler.text()

    def updateInterface(self, index):
        """Update the interface fields with the value from the TreeView"""
        
        if index:       
            tag = self._getResultFromIndex(index)
            
            # selection is an ontology
            if self.entry is None:

                if not self.allow_onto:
                    self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

                # information about ontology is present in memoization table
                if tag in self.onto.keys():
                    
                    self.entry = self.onto[tag]
                    self.ui.value.setPlainText(self.entry['title'])
                    self.ui.prefix.setText(self.entry['preferredPrefix'])
                    self.ui.iri.setPlainText(self.entry['id'])
                    self.ui.description.setPlainText(self.entry['description'])

                # No information is to be found
                else:
                    self.ui.value.setPlainText("")
                    self.ui.prefix.setText("")
                    self.ui.iri.setPlainText("")
                    self.ui.description.setPlainText("")

                self.ui.prefix.setText(tag)
                self.ui.type.setText('Ontology')

            # selection is a class
            else:
                
                self.ui.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)

                self.ui.value.setPlainText(self.entry['label'])
                self.ui.prefix.setText(self.entry['ontology_prefix'])
                self.ui.iri.setPlainText(self.entry['iri'])
                self.ui.type.setText('Class')
                
                self.ui.description.setPlainText(
                    self.entry['description'][0] if 'description' in self.entry else ''
                    )

    def onDoubleClick(self, index):
        """Return class when double clicked"""
        self._getResultFromIndex(index)
        if self.entry is not None:
            self.accept()

    def _memo_onto(self, prefix, jsonconfig):
        self.onto[prefix] = json.loads(jsonconfig)        

if __name__=='__main__':
    app = QApplication(sys.argv)
    ols = OlsDialog()
    ols.exec_()
    print(ols.entry)
    
    
