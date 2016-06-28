# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/colin/dev/HackEdit/hackedit-python/data/forms/settings_page_editor.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.cb_fold_imports = QtWidgets.QCheckBox(self.groupBox)
        self.cb_fold_imports.setObjectName("cb_fold_imports")
        self.verticalLayout_2.addWidget(self.cb_fold_imports)
        self.cb_fold_docstrings = QtWidgets.QCheckBox(self.groupBox)
        self.cb_fold_docstrings.setObjectName("cb_fold_docstrings")
        self.verticalLayout_2.addWidget(self.cb_fold_docstrings)
        self.verticalLayout.addWidget(self.groupBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        from hackedit.api.gettext import get_translation
        _ = get_translation(package="hackedit-python")
        Form.setWindowTitle(_("Form"))
        self.groupBox.setTitle(_("On open"))
        self.cb_fold_imports.setToolTip(_("Fold imports statements when opening a python file."))
        self.cb_fold_imports.setText(_("Fold imports"))
        self.cb_fold_docstrings.setToolTip(_("Fold docstring when opening a python file."))
        self.cb_fold_docstrings.setText(_("Fold docstrings"))

