# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/colin/dev/HackEdit/hackedit-python/data/forms/dlg_create_virtualenv.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(469, 218)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/interpreter-venv.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.edit_name = QtWidgets.QLineEdit(Dialog)
        self.edit_name.setObjectName("edit_name")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.edit_name)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.edit_dir = QtWidgets.QLineEdit(Dialog)
        self.edit_dir.setObjectName("edit_dir")
        self.horizontalLayout.addWidget(self.edit_dir)
        self.bt_dir = QtWidgets.QToolButton(Dialog)
        self.bt_dir.setObjectName("bt_dir")
        self.horizontalLayout.addWidget(self.bt_dir)
        self.formLayout_2.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_4 = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_full_path = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setItalic(True)
        self.label_full_path.setFont(font)
        self.label_full_path.setObjectName("label_full_path")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.label_full_path)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.combo_interpreters = QtWidgets.QComboBox(Dialog)
        self.combo_interpreters.setObjectName("combo_interpreters")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.combo_interpreters)
        self.gridLayout.addLayout(self.formLayout_2, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.check_box_site_packages = QtWidgets.QCheckBox(Dialog)
        self.check_box_site_packages.setObjectName("check_box_site_packages")
        self.gridLayout.addWidget(self.check_box_site_packages, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        from hackedit.api.gettext import get_translation
        _ = get_translation(package="hackedit-python")
        Dialog.setWindowTitle(_("Create virtual environment"))
        self.label.setText(_("Name:"))
        self.edit_name.setToolTip(_("Name of the virtual environment"))
        self.label_2.setText(_("Directory:"))
        self.edit_dir.setToolTip(_("Path where to create the virtual env."))
        self.bt_dir.setToolTip(_("Choose directory"))
        self.bt_dir.setText(_("..."))
        self.label_4.setText(_("Fullpath:"))
        self.label_full_path.setToolTip(_("Full path (Directory + Name)"))
        self.label_full_path.setText(_("path"))
        self.label_3.setText(_("Base interpreter:"))
        self.combo_interpreters.setToolTip(_("Choose the base interpreter to use to create the virtual environment."))
        self.check_box_site_packages.setToolTip(_("Inherit global site-packages"))
        self.check_box_site_packages.setText(_("Inherit global site-packages"))

from . import hackedit_python_rc
