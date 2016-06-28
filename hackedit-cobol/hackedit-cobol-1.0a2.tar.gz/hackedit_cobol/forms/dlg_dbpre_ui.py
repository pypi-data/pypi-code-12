# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/colin/dev/HackEdit/hackedit-cobol/data/forms/dlg_dbpre.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(529, 163)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.edit_exe = PathLineEdit(Dialog)
        self.edit_exe.setObjectName("edit_exe")
        self.horizontalLayout_3.addWidget(self.edit_exe)
        self.bt_exe = QtWidgets.QToolButton(Dialog)
        self.bt_exe.setObjectName("bt_exe")
        self.horizontalLayout_3.addWidget(self.bt_exe)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.edit_obj = PathLineEdit(Dialog)
        self.edit_obj.setObjectName("edit_obj")
        self.horizontalLayout.addWidget(self.edit_obj)
        self.bt_obj = QtWidgets.QToolButton(Dialog)
        self.bt_obj.setObjectName("bt_obj")
        self.horizontalLayout.addWidget(self.bt_obj)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.edit_copy = PathLineEdit(Dialog)
        self.edit_copy.setObjectName("edit_copy")
        self.horizontalLayout_2.addWidget(self.edit_copy)
        self.bt_copy = QtWidgets.QToolButton(Dialog)
        self.bt_copy.setObjectName("bt_copy")
        self.horizontalLayout_2.addWidget(self.bt_copy)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.edit_exe, self.bt_exe)
        Dialog.setTabOrder(self.bt_exe, self.edit_obj)
        Dialog.setTabOrder(self.edit_obj, self.bt_obj)
        Dialog.setTabOrder(self.bt_obj, self.edit_copy)
        Dialog.setTabOrder(self.edit_copy, self.bt_copy)

    def retranslateUi(self, Dialog):
        from hackedit.api.gettext import get_translation
        _ = get_translation(package="hackedit-cobol")
        Dialog.setWindowTitle(_("DBPRE Configuration"))
        self.label.setText(_("Executable:"))
        self.edit_exe.setToolTip(_("Path to the dbpre executable"))
        self.bt_exe.setToolTip(_("Choose the directory that contains the dbpre executable."))
        self.bt_exe.setText(_("..."))
        self.label_2.setText(_("cobmysqlapi.o:"))
        self.edit_obj.setToolTip(_("Path to cobmysqlapi.o"))
        self.bt_obj.setToolTip(_("Choose the directory that contains cobmysqlapi.o"))
        self.bt_obj.setText(_("..."))
        self.label_3.setText(_("Copybooks:"))
        self.edit_copy.setToolTip(_("<html><head/><body><p>Path to the directory that contains the dbpre copybooks.</p></body></html>"))
        self.bt_copy.setToolTip(_("Choose the directory that contains the dbpre copybooks"))
        self.bt_copy.setText(_("..."))

from hackedit.api.widgets import PathLineEdit
