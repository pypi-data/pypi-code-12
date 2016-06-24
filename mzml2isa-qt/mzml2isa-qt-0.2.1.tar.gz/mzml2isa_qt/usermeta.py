#!/usr/bin/env python3

## BACKEND
import os
import sys
import json
from copy import deepcopy

## APP
from mzml2isa.isa import USERMETA
from mzml2isa.versionutils import dict_update

## FRONTEND
from PyQt5.QtWidgets import * #QApplication, QMainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import QPalette, QStandardItemModel, QStandardItem

# UI
from mzml2isa_qt.qt.usermeta import Ui_Dialog as Ui_UserMeta

# UI_MODULES
from mzml2isa_qt.ols import OlsDialog
from mzml2isa_qt.contact import ContactDialog, CONTACT
from mzml2isa_qt.scrapers import PSOThread


# Suffixes for qt fields
SUFFIX = {'study':'', 'investigation':'_2'}


class UserMetaDialog(QDialog):

    SigUpdateMetadata = pyqtSignal('QString')

    def __init__(self, parent=None, metadata={}):

        super(UserMetaDialog, self).__init__(parent)

        self.ui = Ui_UserMeta()
        self.ui.setupUi(self)

        # Update metadata with user submitted ones
        self.metadata = dict_update(USERMETA, metadata)

        # Connect dialog buttons
        self.ui.buttonBox.button(QDialogButtonBox.Apply).clicked.connect(self.save)
        self.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.saveandquit)
        self.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)


        # Connect Contacts buttons
        self.ui.add_contact.clicked.connect(lambda: self.addContact('study'))
        self.ui.rm_contact.clicked.connect(lambda: self.rmContact('study'))
        self.ui.edit_contact.clicked.connect(lambda: self.editContact('study'))
        self.ui.add_contact_2.clicked.connect(lambda: self.addContact('investigation'))
        self.ui.rm_contact_2.clicked.connect(lambda: self.rmContact('investigation'))
        self.ui.edit_contact_2.clicked.connect(lambda: self.editContact('investigation'))

        # Connect Characteristics buttons
        self.ui.search_organism.clicked.connect(lambda: self.searchCharacteristics('organism'))
        self.ui.search_organism_part.clicked.connect(lambda: self.searchCharacteristics('organism_part'))
        self.ui.search_organism_variant.clicked.connect(lambda: self.searchCharacteristics('organism_variant'))
        self.ui.rm_organism.clicked.connect(lambda: self.rmCharacteristics('organism'))                
        self.ui.rm_organism_part.clicked.connect(lambda: self.rmCharacteristics('organism_part'))       
        self.ui.rm_organism_variant.clicked.connect(lambda: self.rmCharacteristics('organism_variant'))

        # Setup Contacts model / view
        self.ui.model_contacts = QStandardItemModel(0,11)
        self.ui.table_contacts.setModel(self.ui.model_contacts)
        self.ui.table_contacts.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.model_contacts_2 = QStandardItemModel(0,11)
        self.ui.table_contacts_2.setModel(self.ui.model_contacts_2)
        self.ui.table_contacts_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Start PSO scraper
        self.PSOscraper = PSOThread()
        self.PSOscraper.Finished.connect(self.fillPSOComboBoxes)
        self.PSOscraper.start()

        # Fill fields with known values
        self.setUpDates()
        self.fillFields()

        self.ui.buttonBox.button(QDialogButtonBox.Apply).setFocus()


    def setUpDates(self):
        """Connect dates changed events"""
        self.dates_changed = {x:False for x in ('s_rel', 's_sub', 'i_rel', 'i_sub')}
        self.ui.submission_date.editingFinished.connect(lambda: self.setDateChanged('s_sub'))
        self.ui.release_date.editingFinished.connect(lambda: self.setDateChanged('s_rel'))
        self.ui.submission_date_2.editingFinished.connect(lambda: self.setDateChanged('i_sub'))
        self.ui.release_date_2.editingFinished.connect(lambda: self.setDateChanged('i_rel'))

    def setDateChanged(self, date):
        """Registers a date was changed."""
        self.dates_changed[date] = True


    def save(self):
        """Save values stored in dialog fields"""
        self.getFields()
        self.SigUpdateMetadata.emit(json.dumps(self.metadata))
        
    def saveandquit(self):
        """Save values and close dialog"""
        self.save()
        self.accept()


    def fillFields(self):
        """Fill dialog fields with known information"""

        ## STUDY
        ### General
        self.ui.title.setText(self.metadata['study']['title'])
        self.ui.description.setPlainText(self.metadata['study']['description'])
        if self.metadata['study']['submission_date']:
            self.ui.submission_date.setDate(QDate.fromString(self.metadata['study']['submission_date'], "yyyy-MM-dd"))
            self.setDateChanged('s_sub')
        if self.metadata['study']['release_date']:
            self.ui.release_date.setDate(QDate.fromString(self.metadata['study']['release_date'], "yyyy-MM-dd"))
            self.setDateChanged('s_rel')
        ### Publication
        self.ui.pubmed_id.setText(self.metadata['study_publication']['pubmed'])
        self.ui.doi.setText(self.metadata['study_publication']['doi'])
        self.ui.pub_title.setText(self.metadata['study_publication']['title'])
        self.ui.authors_list.setPlainText(self.metadata['study_publication']['author_list'])        
        ### Contact
        self.fillContacts(self.metadata['study_contacts'], 'study')

        ## INVESTIGATION
        ### General
        self.ui.identifier_2.setText(self.metadata['investigation']['identifier'])
        self.ui.description_2.setPlainText(self.metadata['investigation']['description'])
        if self.metadata['investigation']['submission_date']:
            self.ui.submission_date_2.setDate(QDate.fromString(self.metadata['investigation']['submission_date'], "yyyy-MM-dd"))
            self.setDateChanged('i_sub')
        if self.metadata['investigation']['release_date']:
            self.ui.release_date_2.setDate(QDate.fromString(self.metadata['investigation']['release_date'], "yyyy-MM-dd"))
            self.setDateChanged('i_rel')
        ### Publication
        self.ui.pubmed_id_2.setText(self.metadata['investigation_publication']['pubmed'])
        self.ui.doi_2.setText(self.metadata['investigation_publication']['doi'])
        self.ui.pub_title_2.setText(self.metadata['investigation_publication']['title'])
        self.ui.authors_list_2.setPlainText(self.metadata['investigation_publication']['author_list'])
        ### Contact
        self.fillContacts(self.metadata['study_contacts'], 'investigation')

        ## EXPERIMENTS
        ## Characteristics
        for key in self.metadata['characteristics'].keys():
            for ontokey in ('value', 'accession', 'ref'):
                getattr(self.ui, ontokey+'_'+key).setText(self.metadata['characteristics'][key][ontokey])

        ### Descriptions
        for (key, value) in self.metadata['description'].items():
            getattr(self.ui, key + '_desc').setPlainText(value)

    def getFields(self):
        """Get intel from dialog fields."""

        ## STUDY
        ### General
        self.metadata['study']['title'] = self.ui.title.text()
        self.metadata['study']['identifier'] = self.ui.identifier.text()
        self.metadata['study']['description'] = self.ui.description.toPlainText()
        self.metadata['study']['submission_date'] = self.ui.submission_date.date().toString("yyyy-MM-dd") if self.dates_changed['s_sub'] else ''
        self.metadata['study']['release_date'] = self.ui.release_date.date().toString("yyyy-MM-dd") if self.dates_changed['s_rel'] else ''
        ### Publication
        self.metadata['study_publication']['pubmed'] = self.ui.pubmed_id.text()
        self.metadata['study_publication']['doi'] = self.ui.doi.text()
        self.metadata['study_publication']['title'] = self.ui.pub_title.text()
        self.metadata['study_publication']['author_list'] = self.ui.authors_list.toPlainText()
        self.metadata['study_publication']['status']['value'] = self.ui.combo_status.currentText() if self.ui.status.text() else ''
        self.metadata['study_publication']['status']['accession'] = self.ui.status.text()
        self.metadata['study_publication']['status']['ref'] = 'PSO' if self.ui.status.text() else ''
        ### Contact
        self.getContactFields('study')

        ## INVESTIGATION
        ### General
        self.metadata['investigation']['identifier'] = self.ui.identifier_2.text()
        self.metadata['investigation']['description'] = self.ui.description_2.toPlainText()
        self.metadata['investigation']['submission_date'] = self.ui.submission_date_2.date().toString("yyyy-MM-dd") if self.dates_changed['i_sub'] else ''
        self.metadata['investigation']['release_date'] = self.ui.release_date_2.date().toString("yyyy-MM-dd") if self.dates_changed['i_rel'] else ''
        ### Publication
        self.metadata['investigation_publication']['pubmed'] = self.ui.pubmed_id_2.text()
        self.metadata['investigation_publication']['doi'] = self.ui.doi_2.text()
        self.metadata['investigation_publication']['title'] = self.ui.pub_title_2.text()
        self.metadata['investigation_publication']['author_list'] = self.ui.authors_list_2.toPlainText()
        self.metadata['investigation_publication']['status']['value'] = self.ui.combo_status_2.currentText() if self.ui.status_2.text() else ""
        self.metadata['investigation_publication']['status']['accession'] = self.ui.status_2.text()
        self.metadata['investigation_publication']['status']['ref'] = 'PSO' if self.ui.status_2.text() else ''
        ### Contact
        self.getContactFields('investigation')

        ## EXPERIMENTS
        ## Characteristics
        for key in self.metadata['characteristics'].keys():
            for ontokey in ('value', 'accession', 'ref'):
                self.metadata['characteristics'][key][ontokey] = getattr(self.ui, ontokey+'_'+key).text()

        ### Descriptions
        for key in self.metadata['description'].keys():
            self.metadata['description'][key] = getattr(self.ui, key+'_desc').toPlainText()


    def getContactFields(self, contact_type):
        """Unified method to get either Study contact or Investigation contact fields"""

        # empty metadata
        self.metadata[contact_type+'_contacts'] = []
        
        #either model_contacts or model_contacts_2
        for row_index in range(getattr(self.ui, 'model_contacts'+SUFFIX[contact_type]).rowCount()):
            self.metadata[contact_type+'_contacts'].append(self.getContactByRow(row_index, contact_type))

        #add default if empty
        if not self.metadata[contact_type+'_contacts']:
            self.metadata[contact_type+'_contacts'].append(dict(deepcopy(CONTACT)))


    def getContactByRow(self, row_index, contact_type):
        contact = deepcopy(CONTACT)
        model = getattr(self.ui, 'model_contacts' + SUFFIX[contact_type])
        for (i, key) in enumerate(contact.keys()):
            if key != 'roles':
                contact[key] = model.item(row_index, i).text()
            else:
                contact[key] = {'accession': model.item(row_index, i).text(),
                                'ref': model.item(row_index, i+1).text(),
                                'value': model.item(row_index, i+2).text()
                               }
        return contact

    def addContact(self, contact_type):
        self.contact = ContactDialog(self)
        self.contact.exec_()
        getattr(self.ui, 'model_contacts' + SUFFIX[contact_type]).appendRow(
            [QStandardItem(self.contact.contact[key]) for key in CONTACT.keys() if key != 'roles'] \
            + [QStandardItem(self.contact.contact['roles'][key]) for key in ('accession', 'ref', 'value')]
        )

    def rmContact(self, contact_type):
        indexes = getattr(self.ui, 'table_contacts'+SUFFIX[contact_type]).selectionModel().selection().indexes()
        if indexes is not None:
            row_index = indexes[0].row()
            getattr(self.ui, 'model_contacts'+SUFFIX[contact_type]).removeRow(row_index)

    def editContact(self, contact_type):
        indexes = getattr(self.ui, 'table_contacts'+SUFFIX[contact_type]).selectionModel().selection().indexes()
        if indexes is not None:
            model = getattr(self.ui, 'model_contacts' + SUFFIX[contact_type])

            row_index = indexes[0].row()
            contact = self.getStudyContactByRow(row_index)
            
            self.contact = ContactDialog(self, json.dumps(contact))
            self.contact.exec_()

            model.removeRow(row_index)
            model.insertRow(row_index,
                [QStandardItem(self.contact.contact[key]) for key in CONTACT.keys() if key != 'roles'] \
                + [QStandardItem(self.contact.contact['roles'][key]) for key in ('accession', 'ref', 'value')]
            )

    def fillContacts(self, contacts, contact_type):
        model = getattr(self.ui, 'model_contacts' + SUFFIX[contact_type]) 
        for contact in contacts:
            if contact != CONTACT:
                model.appendRow(
                    [QStandardItem(contact[key]) for key in CONTACT.keys() if key != 'roles'] \
                    + [QStandardItem(contact['roles'][key]) for key in ('accession', 'ref', 'value')]
                )


    def fillPSOComboBoxes(self, jsontology):
        _translate = QCoreApplication.translate
        # Get PSO ontology
        self.ontoPSO = json.loads(jsontology)
        self.ontoPSOk = sorted(self.ontoPSO)
        # Hide status fields (they ARE useful, though !)
        self.ui.status.hide()
        self.ui.status_2.hide()
        # Hide "connecting to PSO" labels
        self.ui.label_pso.hide()
        self.ui.label_pso_2.hide()
        # Add status to combo box
        for i, status in enumerate(self.ontoPSOk):
            self.ui.combo_status.addItem("")
            self.ui.combo_status.setItemText(i, _translate("Dialog", status))
            self.ui.combo_status_2.addItem("")
            self.ui.combo_status_2.setItemText(i, _translate("Dialog", status))
        # Chek if value to display
        if self.metadata['study_publication']['status']['value']:
            self.ui.combo_status.setCurrentText(self.metadata['study_publication']['status']['value'])
            self.ui.status.setText(self.metadata['study_publication']['status']['accession'])    
        else:
            self.ui.combo_status.setCurrentIndex(-1)   
        if self.metadata['investigation_publication']['status']['value']:
            self.ui.combo_status_2.setCurrentText(self.metadata['investigation_publication']['status']['value'])
            self.ui.status_2.setText(self.metadata['investigation_publication']['status']['accession'])
        else:
            self.ui.combo_status_2.setCurrentIndex(-1)    
        # Link comboboxes and display fields
        self.ui.combo_status.activated.connect(lambda x: self.ui.status.setText(\
          self.ontoPSO[self.ui.combo_status.currentText()]))
        self.ui.combo_status_2.activated.connect(lambda x: self.ui.status_2.setText(\
          self.ontoPSO[self.ui.combo_status_2.currentText()])) 
        # Enable comboboxes
        self.ui.combo_status.setEnabled(True)
        self.ui.combo_status_2.setEnabled(True)


    def searchCharacteristics(self, characteristic):
        """Open an OlsDialog for the right characteristic"""
        self.ols = OlsDialog(self)
        if self.ols.exec_():
            getattr(self.ui, 'value_'+characteristic).setText(self.ols.entry['label'])
            getattr(self.ui, 'ref_'+characteristic).setText(self.ols.entry['ontology_prefix'].upper())
            getattr(self.ui, 'accession_'+characteristic).setText(self.ols.entry['iri'])

    def rmCharacteristics(self, characteristic):
        """Empty given characteristic fields."""
        getattr(self.ui, 'name_'+characteristic).setText('')
        getattr(self.ui, 'ref_'+characteristic).setText('')
        getattr(self.ui, 'iri_'+characteristic).setText('')


if __name__=='__main__':

    app = QApplication(sys.argv)
    um = UserMetaDialog()
    um.SigUpdateMetadata.connect(lambda x: print(x))
    um.show()
    sys.exit(app.exec_())
