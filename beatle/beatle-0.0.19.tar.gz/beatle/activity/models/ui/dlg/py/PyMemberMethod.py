import re
import wx
import wxx
from activity.models.ui import ui as ui
import app.resources as rc
import model.py


# Implementing NewMethod
class PyMemberMethodDialog(ui.NewPyMemberMethod):
    """
    This dialog allows to setup the attributes
    of a member function of python class.
    You can configure the method for not
    generating code at all.
    """
    @wxx.SetInfo(__doc__)
    def __init__(self, parent, container):
        """Initialization"""
        super(PyMemberMethodDialog, self).__init__(parent)
        self.container = container
        self.m_comboBox5.SetFocus()
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(rc.GetBitmap("py_method"))
        self.SetIcon(icon)

    def Validate(self):
        """Validation"""
        self._name = self.m_comboBox5.GetValue()
        if len(self._name) == 0:
            wx.MessageBox("Method name must not be empty", "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, self)
            return False
        if re.match("^[A-Za-z_][0-9A-Za-z_]*$", self._name) is None:
            wx.MessageBox("Method name contains invalid characters", "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, self)
            return False
        self._classmethod = self.m_checkBox21.IsChecked()
        self._staticmethod = self.m_checkBox6.IsChecked()
        self._property = self.m_checkBox41.IsChecked()
        self._note = self.m_richText1.GetValue()
        self._implement = self.m_checkBox86.IsChecked()
        return True

    def get_kwargs(self):
        """Returns kwargs dictionary suitable for object creation"""
        kwargs = {}
        kwargs['parent'] = self.container
        kwargs['name'] = self._name
        kwargs['class_method'] = self._classmethod
        kwargs['static_method'] = self._staticmethod
        kwargs['property'] = self._property
        kwargs['note'] = self._note
        kwargs['implement'] = self._implement
        return kwargs

    def CopyAttributes(self, method):
        """Copy attributes to method"""
        method._name = self._name
        if self._classmethod:
            if not method._classmethod:
                model.py.Decorator(parent=method, name='classmethod')
        elif method._classmethod:
            method._classmethod.Delete()
        if self._staticmethod:
            if not method._staticmethod:
                model.py.Decorator(parent=method, name='staticmethod')
        elif method._staticmethod:
            method._staticmethod.Delete()
        if self._property:
            if not method._property:
                model.py.Decorator(parent=method, name='property')
        elif method._property:
            method._property.Delete()
        method._note = self._note
        method._implement = self._implement

    def SetAttributes(self, method):
        """Setup attributes for editing already method"""
        self.m_comboBox5.SetValue(method._name)
        self.m_checkBox6.SetValue(bool(method._staticmethod))
        self.m_checkBox21.SetValue(bool(method._classmethod))
        self.m_checkBox41.SetValue(bool(method._property))
        self.m_richText1.SetValue(method.note)
        import model.py
        if type(method) is model.py.InitMethod:
            self.SetTitle("Edit __init__ method")
            self.m_comboBox5.Enable(False)
            self.m_checkBox21.Enable(False)
            self.m_checkBox6.Enable(False)
            self.m_checkBox41.Enable(False)
            icon = wx.EmptyIcon()
            icon.CopyFromBitmap(rc.GetBitmap("py_init"))
            self.SetIcon(icon)
        else:
            self.SetTitle("Edit method")
            if len(method[model.py.Argument]) > 1 or method[model.py.ArgsArgument] or method[model.py.KwArgsArgument]:
                self.m_checkBox41.Enable(False)

    # Handlers for NewMethod events.
    def OnCancel(self, event):
        """cancel event handler"""
        self.EndModal(wx.ID_CANCEL)

    def OnOK(self, event):
        """ok event handler"""
        if self.Validate():
            self.EndModal(wx.ID_OK)


