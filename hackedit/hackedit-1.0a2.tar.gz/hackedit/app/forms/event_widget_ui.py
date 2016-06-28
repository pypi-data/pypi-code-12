# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/event_widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 109)
        Form.setMinimumSize(QtCore.QSize(400, 0))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_time = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_time.sizePolicy().hasHeightForWidth())
        self.lbl_time.setSizePolicy(sizePolicy)
        self.lbl_time.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lbl_time.setObjectName("lbl_time")
        self.gridLayout.addWidget(self.lbl_time, 0, 0, 1, 1)
        self.lbl_title = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_title.sizePolicy().hasHeightForWidth())
        self.lbl_title.setSizePolicy(sizePolicy)
        self.lbl_title.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lbl_title.setObjectName("lbl_title")
        self.gridLayout.addWidget(self.lbl_title, 0, 1, 1, 1)
        self.toolButton = QtWidgets.QToolButton(Form)
        self.toolButton.setStyleSheet("border:none;")
        self.toolButton.setText("")
        icon = QtGui.QIcon.fromTheme("window-close")
        self.toolButton.setIcon(icon)
        self.toolButton.setObjectName("toolButton")
        self.gridLayout.addWidget(self.toolButton, 0, 2, 1, 1)
        self.lbl_description = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_description.sizePolicy().hasHeightForWidth())
        self.lbl_description.setSizePolicy(sizePolicy)
        self.lbl_description.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lbl_description.setWordWrap(True)
        self.lbl_description.setObjectName("lbl_description")
        self.gridLayout.addWidget(self.lbl_description, 1, 1, 1, 1)
        self.lbl_pixmap = QtWidgets.QLabel(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_pixmap.sizePolicy().hasHeightForWidth())
        self.lbl_pixmap.setSizePolicy(sizePolicy)
        self.lbl_pixmap.setMinimumSize(QtCore.QSize(0, 0))
        self.lbl_pixmap.setText("")
        self.lbl_pixmap.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lbl_pixmap.setObjectName("lbl_pixmap")
        self.gridLayout.addWidget(self.lbl_pixmap, 1, 0, 1, 1)
        self.lbl_actions = QtWidgets.QLabel(Form)
        self.lbl_actions.setText("")
        self.lbl_actions.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbl_actions.setObjectName("lbl_actions")
        self.gridLayout.addWidget(self.lbl_actions, 2, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lbl_time.setText(_translate("Form", "09:03:30"))
        self.lbl_title.setText(_translate("Form", "Title"))
        self.toolButton.setToolTip(_translate("Form", "Close this notification"))
        self.lbl_description.setText(_translate("Form", "Description"))

from . import hackedit_rc
