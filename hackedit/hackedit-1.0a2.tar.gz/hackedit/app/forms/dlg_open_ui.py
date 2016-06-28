# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/dlg_open.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(435, 146)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.rb_open_new = QtWidgets.QRadioButton(Dialog)
        self.rb_open_new.setChecked(True)
        self.rb_open_new.setObjectName("rb_open_new")
        self.verticalLayout.addWidget(self.rb_open_new)
        self.rb_open_current = QtWidgets.QRadioButton(Dialog)
        self.rb_open_current.setObjectName("rb_open_current")
        self.verticalLayout.addWidget(self.rb_open_current)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label.setText(_translate("Dialog", "How would you like to open the %s?"))
        self.rb_open_new.setToolTip(_translate("Dialog", "Open file/project in a new window"))
        self.rb_open_new.setText(_translate("Dialog", "Open in &new window"))
        self.rb_open_current.setToolTip(_translate("Dialog", "Add project to current window and add it to the list of opened projects."))
        self.rb_open_current.setText(_translate("Dialog", "Open in current window (add &to currently opened projects)"))

