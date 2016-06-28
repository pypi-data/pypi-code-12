# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/dlg_select_workspaces.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(420, 287)
        self.gridLayout_3 = QtWidgets.QGridLayout(Dialog)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.list_workspaces = QtWidgets.QListWidget(self.groupBox)
        self.list_workspaces.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.list_workspaces.setSelectionRectVisible(False)
        self.list_workspaces.setObjectName("list_workspaces")
        self.verticalLayout.addWidget(self.list_workspaces)
        self.lbl_description = QtWidgets.QLabel(self.groupBox)
        self.lbl_description.setScaledContents(False)
        self.lbl_description.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lbl_description.setWordWrap(True)
        self.lbl_description.setObjectName("lbl_description")
        self.verticalLayout.addWidget(self.lbl_description)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout_3.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Select workspace"))
        self.groupBox.setTitle(_translate("Dialog", "Select a workspace"))
        self.list_workspaces.setToolTip(_translate("Dialog", "The list of available workspaces."))
        self.lbl_description.setText(_translate("Dialog", "Workspace description..."))

