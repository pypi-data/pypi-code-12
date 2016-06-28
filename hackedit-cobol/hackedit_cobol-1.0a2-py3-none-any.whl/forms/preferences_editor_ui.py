# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/colin/dev/HackEdit/hackedit-cobol/data/forms/preferences_editor.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(568, 213)
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.rb_lower_case = QtWidgets.QRadioButton(Form)
        self.rb_lower_case.setObjectName("rb_lower_case")
        self.horizontalLayout.addWidget(self.rb_lower_case)
        self.rb_upper_case = QtWidgets.QRadioButton(Form)
        self.rb_upper_case.setChecked(True)
        self.rb_upper_case.setObjectName("rb_upper_case")
        self.horizontalLayout.addWidget(self.rb_upper_case)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.edit_comment = QtWidgets.QLineEdit(Form)
        self.edit_comment.setObjectName("edit_comment")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.edit_comment)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        from hackedit.api.gettext import get_translation
        _ = get_translation(package="hackedit-cobol")
        Form.setWindowTitle(_("Form"))
        self.label_2.setText(_("Proposed keywords:"))
        self.rb_lower_case.setToolTip(_("Propose COBOL keyword in lower-case."))
        self.rb_lower_case.setText(_("&lower-case"))
        self.rb_upper_case.setToolTip(_("Propose COBOL keyword in UPPER-CASE.."))
        self.rb_upper_case.setText(_("&UPPER-CASE"))
        self.label_3.setText(_("Comment symbol:"))
        self.edit_comment.setToolTip(_("The comment indicator."))
        self.edit_comment.setText(_("*> "))

