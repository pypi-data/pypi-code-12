# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/service.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 160)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 30, 120, 20))
        self.label.setObjectName(_fromUtf8("label"))
        self.input_service_id = QtGui.QLineEdit(self.centralwidget)
        self.input_service_id.setGeometry(QtCore.QRect(80, 30, 113, 20))
        self.input_service_id.setText(_fromUtf8(""))
        self.input_service_id.setObjectName(_fromUtf8("input_service_id"))
        self.label1 = QtGui.QLabel(self.centralwidget)
        self.label1.setGeometry(QtCore.QRect(10, 60, 120, 20))
        self.label1.setObjectName(_fromUtf8("label1"))
        self.input_name = QtGui.QLineEdit(self.centralwidget)
        self.input_name.setGeometry(QtCore.QRect(80, 60, 113, 20))
        self.input_name.setText(_fromUtf8(""))
        self.input_name.setObjectName(_fromUtf8("input_name"))
        self.label2 = QtGui.QLabel(self.centralwidget)
        self.label2.setGeometry(QtCore.QRect(10, 90, 120, 20))
        self.label2.setObjectName(_fromUtf8("label2"))
        self.input_img = QtGui.QLineEdit(self.centralwidget)
        self.input_img.setGeometry(QtCore.QRect(80, 90, 113, 20))
        self.input_img.setText(_fromUtf8(""))
        self.input_img.setObjectName(_fromUtf8("input_img"))
        self.label3 = QtGui.QLabel(self.centralwidget)
        self.label3.setGeometry(QtCore.QRect(10, 120, 120, 20))
        self.label3.setObjectName(_fromUtf8("label3"))
        self.input_description = QtGui.QLineEdit(self.centralwidget)
        self.input_description.setGeometry(QtCore.QRect(80, 120, 113, 20))
        self.input_description.setText(_fromUtf8(""))
        self.input_description.setObjectName(_fromUtf8("input_description"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.label.setText(_translate("MainWindow", "service_id", None))
        self.label1.setText(_translate("MainWindow", "name", None))
        self.label2.setText(_translate("MainWindow", "img", None))
        self.label3.setText(_translate("MainWindow", "description", None))

