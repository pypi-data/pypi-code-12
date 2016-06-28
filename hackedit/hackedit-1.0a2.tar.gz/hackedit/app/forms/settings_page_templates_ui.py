# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/home/colin/Documents/hackedit/data/forms/settings_page_templates.ui'
#
# Created by: PyQt5 UI code generator 5.6.1.dev1604260930
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(865, 626)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(6, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_2 = QtWidgets.QGroupBox(Form)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.list_sources = QtWidgets.QListWidget(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.list_sources.sizePolicy().hasHeightForWidth())
        self.list_sources.setSizePolicy(sizePolicy)
        self.list_sources.setObjectName("list_sources")
        self.verticalLayout_2.addWidget(self.list_sources)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.bt_add_source = QtWidgets.QPushButton(self.groupBox_2)
        icon = QtGui.QIcon.fromTheme("list-add")
        self.bt_add_source.setIcon(icon)
        self.bt_add_source.setObjectName("bt_add_source")
        self.horizontalLayout_2.addWidget(self.bt_add_source)
        self.bt_rm_source = QtWidgets.QPushButton(self.groupBox_2)
        icon = QtGui.QIcon.fromTheme("list-remove")
        self.bt_rm_source.setIcon(icon)
        self.bt_rm_source.setObjectName("bt_rm_source")
        self.horizontalLayout_2.addWidget(self.bt_rm_source)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.group_details = QtWidgets.QGroupBox(Form)
        self.group_details.setObjectName("group_details")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.group_details)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.list_templates = QtWidgets.QListWidget(self.group_details)
        self.list_templates.setObjectName("list_templates")
        self.verticalLayout_3.addWidget(self.list_templates)
        self.horizontalLayout.addWidget(self.group_details)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        from hackedit.api.gettext import get_translation
        _ = get_translation(package="hackedit")
        Form.setWindowTitle(_("Form"))
        self.groupBox_2.setTitle(_("Sources"))
        self.bt_add_source.setToolTip(_("Add a template source"))
        self.bt_add_source.setText(_("Add"))
        self.bt_rm_source.setToolTip(_("Remove template source"))
        self.bt_rm_source.setText(_("Remove"))
        self.group_details.setTitle(_("Templates"))

