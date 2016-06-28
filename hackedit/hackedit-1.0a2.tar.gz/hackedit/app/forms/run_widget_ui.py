# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/run_widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(454, 326)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setContentsMargins(6, 6, 6, 6)
        self.gridLayout.setSpacing(3)
        self.gridLayout.setObjectName("gridLayout")
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 0, 2, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.bt_run = QtWidgets.QToolButton(Form)
        self.bt_run.setText("")
        icon = QtGui.QIcon.fromTheme("system-run")
        self.bt_run.setIcon(icon)
        self.bt_run.setObjectName("bt_run")
        self.verticalLayout.addWidget(self.bt_run)
        self.bt_pin = QtWidgets.QToolButton(Form)
        self.bt_pin.setText("")
        icon = QtGui.QIcon.fromTheme("object-locked")
        self.bt_pin.setIcon(icon)
        self.bt_pin.setCheckable(True)
        self.bt_pin.setChecked(False)
        self.bt_pin.setObjectName("bt_pin")
        self.verticalLayout.addWidget(self.bt_pin)
        self.bt_print = QtWidgets.QToolButton(Form)
        self.bt_print.setText("")
        icon = QtGui.QIcon.fromTheme("document-print")
        self.bt_print.setIcon(icon)
        self.bt_print.setObjectName("bt_print")
        self.verticalLayout.addWidget(self.bt_print)
        self.bt_clear = QtWidgets.QToolButton(Form)
        self.bt_clear.setText("")
        icon = QtGui.QIcon.fromTheme("user-trash")
        self.bt_clear.setIcon(icon)
        self.bt_clear.setObjectName("bt_clear")
        self.verticalLayout.addWidget(self.bt_clear)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setObjectName("tabWidget")
        self.gridLayout.addWidget(self.tabWidget, 0, 3, 1, 1)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.bt_run.setToolTip(_translate("Form", "Run current tab"))
        self.bt_pin.setToolTip(_translate("Form", "Pin/Unpin current tab"))
        self.bt_print.setToolTip(_translate("Form", "Print current tab"))
        self.bt_clear.setToolTip(_translate("Form", "Clear current output"))

