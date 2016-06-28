from PyQt5 import QtCore, QtWidgets

from hackedit.app.forms import dlg_template_vars_ui


class DlgTemplateVars(QtWidgets.QDialog):
    def __init__(self, variables, parent=None):
        super().__init__(parent=parent)
        self.ui = dlg_template_vars_ui.Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.tableWidget.clearContents()
        self.ui.tableWidget.setRowCount(0)
        for variable in sorted(variables, key=lambda item: item['display']):
            index = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(index)
            item = QtWidgets.QTableWidgetItem()
            item.setText(variable['display'])
            self.ui.tableWidget.setItem(index, 0, item)
            item = QtWidgets.QTableWidgetItem()
            item.setData(QtCore.Qt.UserRole, variable)
            try:
                item.setText(variable['default'])
            except KeyError:
                item.setText('')
            self.ui.tableWidget.setItem(index, 1, item)
        self.adjustSize()

    @classmethod
    def get_answers(cls, variables, parent=None):
        dlg = DlgTemplateVars(variables, parent=parent)
        ret_val = None
        if dlg.exec_() == dlg.Accepted:
            ret_val = {}
            for i in range(dlg.ui.tableWidget.rowCount()):
                item = dlg.ui.tableWidget.item(i, 1)
                data = item.data(QtCore.Qt.UserRole)
                ret_val[data['name']] = item.text()
        return ret_val
