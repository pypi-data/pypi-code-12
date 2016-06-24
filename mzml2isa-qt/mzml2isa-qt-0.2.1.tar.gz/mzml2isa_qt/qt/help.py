# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/help.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HelpWindow(object):
    def setupUi(self, HelpWindow):
        HelpWindow.setObjectName("HelpWindow")
        HelpWindow.resize(514, 376)
        self.buttonBox = QtWidgets.QDialogButtonBox(HelpWindow)
        self.buttonBox.setGeometry(QtCore.QRect(300, 270, 191, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.helpList = QtWidgets.QListWidget(HelpWindow)
        self.helpList.setGeometry(QtCore.QRect(10, 10, 181, 301))
        self.helpList.setObjectName("helpList")

        self.retranslateUi(HelpWindow)
        self.buttonBox.accepted.connect(HelpWindow.accept)
        self.buttonBox.rejected.connect(HelpWindow.reject)
        QtCore.QMetaObject.connectSlotsByName(HelpWindow)

    def retranslateUi(self, HelpWindow):
        _translate = QtCore.QCoreApplication.translate
        HelpWindow.setWindowTitle(_translate("HelpWindow", "Dialog"))

