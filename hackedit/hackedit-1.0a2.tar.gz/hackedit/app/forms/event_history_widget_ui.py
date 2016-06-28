# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/event_history_widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(518, 279)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self._ = QtWidgets.QVBoxLayout()
        self._.setObjectName("_")
        self.bt_clear = QtWidgets.QToolButton(Form)
        icon = QtGui.QIcon.fromTheme("edit-clear")
        self.bt_clear.setIcon(icon)
        self.bt_clear.setObjectName("bt_clear")
        self._.addWidget(self.bt_clear)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self._.addItem(spacerItem)
        self.horizontalLayout.addLayout(self._)
        self.scrollArea = QtWidgets.QScrollArea(Form)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 462, 263))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.scrollAreaWidgetContents)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.vertical_layout.setObjectName("vertical_layout")
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.vertical_layout.addItem(spacerItem1)
        self.gridLayout.addLayout(self.vertical_layout, 1, 0, 1, 1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.bt_clear.setToolTip(_translate("Form", "Clear history"))
        self.bt_clear.setText(_translate("Form", "..."))

