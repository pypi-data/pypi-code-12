# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/dlg_preferences.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(933, 726)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/Preferences-system.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.categories = QtWidgets.QTreeWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.categories.sizePolicy().hasHeightForWidth())
        self.categories.setSizePolicy(sizePolicy)
        self.categories.setMinimumSize(QtCore.QSize(250, 0))
        self.categories.setIconSize(QtCore.QSize(22, 22))
        self.categories.setObjectName("categories")
        self.categories.header().setVisible(False)
        self.horizontalLayout.addWidget(self.categories)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_title = QtWidgets.QLabel(Dialog)
        self.label_title.setStyleSheet("background-color: palette(highlight);\n"
"color: palette(highlighted-text);\n"
"padding: 10px;\n"
"border-radius:3px;")
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.verticalLayout_2.addWidget(self.label_title)
        self.pages = QtWidgets.QStackedWidget(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pages.sizePolicy().hasHeightForWidth())
        self.pages.setSizePolicy(sizePolicy)
        self.pages.setObjectName("pages")
        self.verticalLayout_2.addWidget(self.pages)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttons = QtWidgets.QDialogButtonBox(Dialog)
        self.buttons.setOrientation(QtCore.Qt.Horizontal)
        self.buttons.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok|QtWidgets.QDialogButtonBox.Reset|QtWidgets.QDialogButtonBox.RestoreDefaults)
        self.buttons.setCenterButtons(False)
        self.buttons.setObjectName("buttons")
        self.verticalLayout.addWidget(self.buttons)

        self.retranslateUi(Dialog)
        self.buttons.accepted.connect(Dialog.accept)
        self.buttons.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Preferences"))
        self.categories.setToolTip(_translate("Dialog", "Categories"))
        self.categories.headerItem().setText(0, _translate("Dialog", "item"))
        self.label_title.setText(_translate("Dialog", "Page title"))
        self.buttons.setToolTip(_translate("Dialog", "<html><head/><body><p>Ok: Apply settings and quit the dialog</p><p>Cancel: Quit the dialog without applying the settings</p><p>Reset: reset the value of the changed settings of the current page (cancel any changes you\'ve made)</p><p>Restore defaults: restore the initial default values of the current page</p></body></html>"))

