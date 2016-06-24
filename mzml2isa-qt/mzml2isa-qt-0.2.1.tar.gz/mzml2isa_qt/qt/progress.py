# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/progress.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(640, 140)
        Dialog.setMinimumSize(QtCore.QSize(640, 140))
        Dialog.setMaximumSize(QtCore.QSize(640, 140))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/graphics/assets/graphics/ebi_icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Dialog.setWindowIcon(icon)
        Dialog.setSizeGripEnabled(False)
        Dialog.setModal(False)
        self.pBar_parse = QtWidgets.QProgressBar(Dialog)
        self.pBar_parse.setGeometry(QtCore.QRect(10, 55, 620, 25))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(11, 123, 125))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(11, 123, 125))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(209, 209, 209))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, brush)
        self.pBar_parse.setPalette(palette)
        self.pBar_parse.setStyleSheet("font: 12pt url(:/fonts/assets/fonts/Verdana.ttf);")
        self.pBar_parse.setMaximum(0)
        self.pBar_parse.setProperty("value", 0)
        self.pBar_parse.setAlignment(QtCore.Qt.AlignCenter)
        self.pBar_parse.setObjectName("pBar_parse")
        self.pBar_studies = QtWidgets.QProgressBar(Dialog)
        self.pBar_studies.setGeometry(QtCore.QRect(10, 20, 620, 25))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pBar_studies.sizePolicy().hasHeightForWidth())
        self.pBar_studies.setSizePolicy(sizePolicy)
        self.pBar_studies.setSizeIncrement(QtCore.QSize(0, 0))
        self.pBar_studies.setStyleSheet("font: 12pt url(:/fonts/assets/fonts/Verdana.ttf);")
        self.pBar_studies.setMaximum(0)
        self.pBar_studies.setProperty("value", 0)
        self.pBar_studies.setAlignment(QtCore.Qt.AlignCenter)
        self.pBar_studies.setObjectName("pBar_studies")
        self.label_study = QtWidgets.QLabel(Dialog)
        self.label_study.setGeometry(QtCore.QRect(10, 20, 620, 25))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_study.sizePolicy().hasHeightForWidth())
        self.label_study.setSizePolicy(sizePolicy)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(11, 122, 124))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(11, 122, 124))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Highlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(209, 209, 209))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Highlight, brush)
        self.label_study.setPalette(palette)
        self.label_study.setAutoFillBackground(False)
        self.label_study.setStyleSheet("font: 12pt url(:/fonts/assets/fonts/Verdana.ttf);")
        self.label_study.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_study.setObjectName("label_study")
        self.textEdit_filename = QtWidgets.QTextEdit(Dialog)
        self.textEdit_filename.setGeometry(QtCore.QRect(9, 95, 620, 25))
        font = QtGui.QFont()
        font.setFamily("Monospace")
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.textEdit_filename.setFont(font)
        self.textEdit_filename.setStyleSheet("background-color: rgb(0, 0, 0);\n"
"font: 10pt \"Monospace\";\n"
"color: rgb(255,255,255);")
        self.textEdit_filename.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.textEdit_filename.setObjectName("textEdit_filename")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pBar_parse.setFormat(_translate("Dialog", "%v / %m files parsed"))
        self.pBar_studies.setFormat(_translate("Dialog", "%v / %m studies parsed"))
        self.label_study.setText(_translate("Dialog", "TextLabel"))

import resources_rc
