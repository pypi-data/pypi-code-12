# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/settings_page_shortcuts.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(505, 355)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.edit_filter = PromptLineEdit(Form)
        self.edit_filter.setObjectName("edit_filter")
        self.verticalLayout.addWidget(self.edit_filter)
        self.table = QtWidgets.QTableWidget(Form)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setObjectName("table")
        self.table.setColumnCount(2)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        self.table.horizontalHeader().setCascadingSectionResizes(False)
        self.table.verticalHeader().setVisible(False)
        self.verticalLayout.addWidget(self.table)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.edit_filter.setToolTip(_translate("Form", "Filter actions by name or by shortcut"))
        self.table.setToolTip(_translate("Form", "The list of application shortcuts"))
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Action"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Shortcut"))

from pyqode.core.widgets import PromptLineEdit
