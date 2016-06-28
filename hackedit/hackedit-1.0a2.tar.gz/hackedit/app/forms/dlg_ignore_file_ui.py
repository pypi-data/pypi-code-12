# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/Colin/Documents/hackedit/data/forms/dlg_ignore_file.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 113)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.rb_explicit = QtWidgets.QRadioButton(Dialog)
        self.rb_explicit.setChecked(True)
        self.rb_explicit.setObjectName("rb_explicit")
        self.verticalLayout.addWidget(self.rb_explicit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.rb_pattern = QtWidgets.QRadioButton(Dialog)
        self.rb_pattern.setObjectName("rb_pattern")
        self.horizontalLayout.addWidget(self.rb_pattern)
        self.edit_pattern = QtWidgets.QLineEdit(Dialog)
        self.edit_pattern.setEnabled(False)
        self.edit_pattern.setObjectName("edit_pattern")
        self.horizontalLayout.addWidget(self.edit_pattern)
        self.verticalLayout.addLayout(self.horizontalLayout)
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
        self.rb_pattern.toggled['bool'].connect(self.edit_pattern.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Mark as ignored"))
        self.rb_explicit.setToolTip(_translate("Dialog", "Ignore explicitely"))
        self.rb_explicit.setText(_translate("Dialog", "I&gnore explicitely (e.g. \'file.obj\')"))
        self.rb_pattern.setToolTip(_translate("Dialog", "Use an ignore pattern"))
        self.rb_pattern.setText(_translate("Dialog", "Ignore as pa&ttern (e.g. \'*.obj\')"))
        self.edit_pattern.setToolTip(_translate("Dialog", "Ignore pattern"))

