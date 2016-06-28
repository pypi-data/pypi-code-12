# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/task_widget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(456, 114)
        Form.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.group = QtWidgets.QGroupBox(Form)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.group.sizePolicy().hasHeightForWidth())
        self.group.setSizePolicy(sizePolicy)
        self.group.setObjectName("group")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.group)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.bt_cancel = QtWidgets.QToolButton(self.group)
        icon = QtGui.QIcon.fromTheme("process-stop")
        self.bt_cancel.setIcon(icon)
        self.bt_cancel.setObjectName("bt_cancel")
        self.gridLayout_2.addWidget(self.bt_cancel, 0, 1, 1, 1)
        self.pbar_progress = QtWidgets.QProgressBar(self.group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pbar_progress.sizePolicy().hasHeightForWidth())
        self.pbar_progress.setSizePolicy(sizePolicy)
        self.pbar_progress.setMinimumSize(QtCore.QSize(0, 0))
        self.pbar_progress.setMaximum(0)
        self.pbar_progress.setProperty("value", -1)
        self.pbar_progress.setTextVisible(True)
        self.pbar_progress.setObjectName("pbar_progress")
        self.gridLayout_2.addWidget(self.pbar_progress, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbl_description = ElidedLabel(self.group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_description.sizePolicy().hasHeightForWidth())
        self.lbl_description.setSizePolicy(sizePolicy)
        self.lbl_description.setMinimumSize(QtCore.QSize(350, 0))
        self.lbl_description.setMaximumSize(QtCore.QSize(350, 16777215))
        self.lbl_description.setWordWrap(False)
        self.lbl_description.setObjectName("lbl_description")
        self.horizontalLayout.addWidget(self.lbl_description)
        spacerItem = QtWidgets.QSpacerItem(32, 20, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.gridLayout_2.addLayout(self.horizontalLayout, 1, 0, 1, 1)
        self.gridLayout.addWidget(self.group, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.group.setTitle(_translate("Form", "Name"))
        self.bt_cancel.setToolTip(_translate("Form", "Cancel operation"))
        self.bt_cancel.setText(_translate("Form", "..."))
        self.lbl_description.setText(_translate("Form", "Description"))

from hackedit.api.widgets import ElidedLabel
