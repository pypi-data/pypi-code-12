# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/locator.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Frame(object):
    def setupUi(self, Frame):
        Frame.setObjectName("Frame")
        Frame.resize(698, 274)
        Frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        Frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.verticalLayout = QtWidgets.QVBoxLayout(Frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.bt_infos = QtWidgets.QToolButton(Frame)
        icon = QtGui.QIcon.fromTheme("dialog-information")
        self.bt_infos.setIcon(icon)
        self.bt_infos.setObjectName("bt_infos")
        self.horizontalLayout.addWidget(self.bt_infos)
        self.lineEdit = PromptLineEdit(Frame)
        self.lineEdit.setMinimumSize(QtCore.QSize(400, 0))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.bt_close = QtWidgets.QToolButton(Frame)
        icon = QtGui.QIcon.fromTheme("window-close")
        self.bt_close.setIcon(icon)
        self.bt_close.setObjectName("bt_close")
        self.horizontalLayout.addWidget(self.bt_close)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.treeWidget = QtWidgets.QTreeWidget(Frame)
        self.treeWidget.setMaximumSize(QtCore.QSize(16777215, 500))
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.verticalLayout.addWidget(self.treeWidget)
        self.cb_non_project_files = QtWidgets.QCheckBox(Frame)
        self.cb_non_project_files.setObjectName("cb_non_project_files")
        self.verticalLayout.addWidget(self.cb_non_project_files)

        self.retranslateUi(Frame)
        QtCore.QMetaObject.connectSlotsByName(Frame)

    def retranslateUi(self, Frame):
        _translate = QtCore.QCoreApplication.translate
        Frame.setWindowTitle(_translate("Frame", "Frame"))
        self.bt_infos.setToolTip(_translate("Frame", "Help"))
        self.bt_infos.setText(_translate("Frame", "..."))
        self.bt_close.setToolTip(_translate("Frame", "Close"))
        self.bt_close.setText(_translate("Frame", "..."))
        self.cb_non_project_files.setText(_translate("Frame", "Include non-project files (Shift+Enter)"))

from pyqode.core.widgets import PromptLineEdit
