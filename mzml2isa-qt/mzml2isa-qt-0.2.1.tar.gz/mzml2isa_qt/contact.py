#!/usr/bin/env python3

## BACKEND
import sys
import os
import json
from copy import deepcopy
from collections import OrderedDict

## FRONTEND
from PyQt5.QtWidgets import * 
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette

## APP
from mzml2isa.versionutils import dict_update

## UI
from mzml2isa_qt.qt.contact import Ui_Dialog as Ui_Contact

## UI MODULES
from mzml2isa_qt.scrapers import PROThread



# Default contact dict
CONTACT = OrderedDict([
			('first_name', ''), ('mid', ''), ('last_name',''),
			('phone',''), ('email',''), ('fax',''), ('affiliation',''),
			('adress',''), 
			('roles',{'accession':'', 'ref':'', 'value':''}),
		  ])



class ContactDialog(QDialog):
    """Add or edit a contact"""

    def __init__(self, parent=None, jsoncontact=None):
        super(ContactDialog, self).__init__(parent)
        self.ui = Ui_Contact()
        self.ui.setupUi(self)

        # Launch Publishing Roles Ontology scraper
        self.PROscraper = PROThread()
        self.PROscraper.Finished.connect(self.fillPROComboBox)
        self.PROscraper.start()

        # Connect buttons
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.onOkClicked)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

        # Try to load existing contact info & fill fields
        self.contact = json.loads(jsoncontact) if jsoncontact is not None else dict(deepcopy(CONTACT))
        self.fillFields()

        self.ui.first_name.setFocus()

    def fillFields(self):
        """Fill fields with known information"""
        for (key, value) in self.contact.items():
            if key not in ('roles', 'adress'):
                getattr(self.ui, key).setText(value)
            elif key == 'adress':
                self.ui.adress.setPlainText(value)

    def fillPROComboBox(self, jsontology):
        """Fill pro combobox with scraped information"""
        _translate = QCoreApplication.translate
        # Get PRO ontology
        self.ontoPRO = json.loads(jsontology)
        self.ontoPROk = sorted(self.ontoPRO)
        # Hide roles fields (they ARE useful, though !)
        self.ui.roles.hide()
        # Hide "connecting to PRO" labels
        self.ui.label_pro.hide()
        # Add status to combo box
        for i, status in enumerate(self.ontoPROk):
            self.ui.combo_roles.addItem("")
            self.ui.combo_roles.setItemText(i, _translate("Dialog", status))
        # Check if value to display
        if self.contact['roles']['value']:
            self.ui.combo_roles.setCurrentText(self.contact['roles']['value'])
            self.ui.roles.setText(self.contact['roles']['accession'])
        else:
            self.ui.combo_roles.setCurrentIndex(-1)
            self.ui.roles.setText('')
        # Link comboboxes and display fields
        self.ui.combo_roles.activated.connect(lambda x: self.ui.roles.setText(\
          self.ontoPRO[self.ui.combo_roles.currentText()]))
        # Enable comboboxes
        self.ui.combo_roles.setEnabled(True)

    def getFields(self):
        """Get contact information from Dialog fields"""
        for key in self.contact.keys():
            if key not in ('roles', 'adress'):
                self.contact[key] = getattr(self.ui, key).text() or ''
            elif key == 'adress':
                self.contact['adress'] = self.ui.adress.toPlainText() or ''

        self.contact['roles']['value'] = self.ui.combo_roles.currentText() if self.ui.roles.text() else ''
        self.contact['roles']['accession'] = self.ui.roles.text()
        self.contact['roles']['ref'] = 'PRO' if self.ui.roles.text() else ''

    def onOkClicked(self):
        self.getFields()
        self.accept()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    um = ContactDialog()
    um.exec_()
    um = ContactDialog()
    um.exec_()
    print(um.contact)
