#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..qtbase import QtCore
from ..qtbase import QtWidgets

from ..tests import get_system_info

class DebugInfoWidget(QtWidgets.QTreeWidget):

    def __init__(self, main_window, parent = None):
        super(DebugInfoWidget, self).__init__(parent)
        self.setWindowTitle('Debug information')
        self.setGeometry(QtCore.QRect(100, 100, 500, 800))

        dinfo = get_system_info(pretty_print=False)

        header = QtWidgets.QTreeWidgetItem(["Parameter", "Value"])
        self.setHeaderItem(header) 

        for sec_key, sec_value in dinfo.items():
            header = QtWidgets.QTreeWidgetItem(self, [sec_key])
            header.setExpanded(True)

            for key in sorted(sec_value):
                val = sec_value[key]
                label = str(val)
                QtWidgets.QTreeWidgetItem(header, [key, label])

            self.base = main_window
            self.header().resizeSection(0, 230)


    def closeEvent(self, event):
        self.base.widgets['info'] = None
        super(DebugInfoWidget, self).closeEvent(event)
