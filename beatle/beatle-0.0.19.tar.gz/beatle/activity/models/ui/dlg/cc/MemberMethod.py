import re
import copy
import wx
import wxx
import model
from activity.models.ui import ui as ui
import app.resources as rc


# Implementing NewMethod
class MemberMethodDialog(ui.NewMemberMethod):
    """
    This dialog allows to setup the attributes
    of a member function of struct or class.
    You can configure the method for not write
    his declaration and/or his implementation.
    """
    @wxx.SetInfo(__doc__)
    def __init__(self, parent, container):
        """Initialization"""
        super(MemberMethodDialog, self).__init__(parent)
        self.container = container

        #new code for types
        self._types = dict([x._name, x] for x in container.types)
        self.m_choice1.AppendItems([x for x in self._types.keys() if x != '@'])

        self._template_types = []
        # we need to add types from template nested classes
        self._nested_template_types = container.template_types
        if len(self._nested_template_types) > 0:
            self.m_choice1.AppendItems(self._nested_template_types)
        self.m_choice1.SetSelection(self.m_choice1.FindString(''))
        self.choiceStr = ""
        self.m_comboBox5.SetFocus()
        icon = wx.EmptyIcon()
        icon.CopyFromBitmap(rc.GetBitmap("method"))
        self.SetIcon(icon)

    def OnToggleTemplate(self, event):
        """Handles toggle event"""
        if self.m_checkBox63.GetValue():
            self.m_stStartTemplate.Enable(True)
            self.m_template.Enable(True)
            self.m_stEndTemplate.Enable(True)
            # templates cannot be virtual
            self.m_checkBox11.SetValue(False)
            self.m_checkBox11.Enable(False)
            self.m_checkBox21.SetValue(False)
            self.m_checkBox21.Enable(False)
        else:
            self.m_stStartTemplate.Enable(False)
            self.m_template.SetValue('')
            self.m_template.Enable(False)
            self.m_stEndTemplate.Enable(False)
            # non-templates can be virtual
            self.m_checkBox11.Enable(True)
            self.m_checkBox21.Enable(True)
        event.Skip()

    def removeTemplateTypes(self):
        """Remove template generated types from combo. This method only removes
        the in-place template types created by function template declaration."""
        # get current value
        iSel = self.m_choice1.GetCurrentSelection()
        if iSel != wx.NOT_FOUND:
            s = self.m_choice1.GetString(iSel)
        else:
            s = None
        for x in self._template_types:
            i = self.m_choice1.FindString(x)
            if i != wx.NOT_FOUND:
                self.m_choice1.Delete(i)
        if s is not None:
            self.m_choice1.SetStringSelection(s)

    def OnChangeTemplateSpecification(self, event):
        """Handles change text event"""
        # When the template specification changes, virtual types must be added
        text = self.m_template.GetValue()
        l = text.split(',')
        prologs = ['class', 'typename']
        r = []
        for u in l:
            v = u.split('=')[0].strip()
            for p in prologs:
                if v.find(p) == 0:
                    v = v.replace(p, '').strip()
                    if len(v) and v not in self._nested_template_types:
                        r.append(v)
                    break
        #remove previous template types
        self.removeTemplateTypes()
        # Append templates to available types
        if len(r):
            self.m_choice1.AppendItems(r)
            self._template_types = r
        event.Skip()

    def OnTypeChanged(self, event):
        """This event happens when the return type is changed. The main goal
        of this callback is handling template types for argument specification"""
        iSel = self.m_choice1.GetCurrentSelection()
        _type = self._types.get(self.m_choice1.GetString(iSel), None)
        template_args = False
        if _type is not None:
            if _type._template is not None:
                template_args = True
        if template_args is True:
            self.m_staticText65.Enable(True)
            self.m_template_args.Enable(True)
            self.m_staticText66.Enable(True)
        else:
            self.m_staticText65.Enable(False)
            self.m_template_args.Enable(False)
            self.m_staticText66.Enable(False)
            self.m_template_args.SetValue('')
        event.Skip()

    def Validate(self):
        """Validation"""
        self._name = self.m_comboBox5.GetValue()
        if len(self._name) == 0:
            wx.MessageBox("Method name must not be empty", "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, self)
            return False
        if re.match("^([A-Za-z_][0-9A-Za-z_]*|operator (=|==|!=|<|>|<=|>=|\+|-|\*|/|%|\+=|-=|\*=|/=|%=|!|&&|\|\||\+\+|--|&|\||\^|~|&=|\|=|\^=|<<|>>|<<=|>>=|->|\(\)|\[\]|new|delete|bool|int))$", self._name) is None:
            wx.MessageBox("Method name contains invalid characters", "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, self)
            return False
        iSel = self.m_choice1.GetCurrentSelection()
        if iSel == wx.NOT_FOUND:
            wx.MessageBox("Invalid type", "Error",
                wx.OK | wx.CENTER | wx.ICON_ERROR, self)
            return False
        typename = self.m_choice1.GetString(iSel)
        if self.m_checkBox63.IsChecked():
            self._template = self.m_template.GetValue()
        else:
            self._template = None
        #filter template types
        template_types = self._template_types + self._nested_template_types
        if typename in template_types:
            self._typei = model.cc.typeinst(
                type=self._types['@'],
                type_alias=typename,
                const=self.m_checkBox1.IsChecked(),
                ptr=self.m_checkBox3.IsChecked(),
                ref=self.m_checkBox2.IsChecked(),
                ptrptr=self.m_checkBox4.IsChecked(),
                constptr=self.m_checkBox5.IsChecked(),
                )
        else:
            _type = self._types[typename]
            if _type._template is not None:
                #we construct type instance with explicit arguments
                type_args = self.m_template_args.GetValue()
                self._typei = model.cc.typeinst(
                    type=_type,
                    const=self.m_checkBox1.IsChecked(),
                    ptr=self.m_checkBox3.IsChecked(),
                    ref=self.m_checkBox2.IsChecked(),
                    ptrptr=self.m_checkBox4.IsChecked(),
                    constptr=self.m_checkBox5.IsChecked(),
                    type_args=type_args
                    )
            else:
                self._typei = model.cc.typeinst(
                    type=_type,
                    const=self.m_checkBox1.IsChecked(),
                    ptr=self.m_checkBox3.IsChecked(),
                    ref=self.m_checkBox2.IsChecked(),
                    ptrptr=self.m_checkBox4.IsChecked(),
                    constptr=self.m_checkBox5.IsChecked(),
                    )
        iSel = self.m_choice2.GetCurrentSelection()
        self._access = self.m_choice2.GetString(iSel)
        self._static = self.m_checkBox6.IsChecked()
        self._virtual = self.m_checkBox11.IsChecked()
        self._pure = self.m_checkBox21.IsChecked()
        self._inline = self.m_checkBox31.IsChecked()
        self._const_method = self.m_checkBox41.IsChecked()
        self._note = self.m_richText1.GetValue()
        self._declare = self.m_checkBox85.IsChecked()
        self._implement = self.m_checkBox86.IsChecked()
        return True

    def get_kwargs(self):
        """Returns kwargs dictionary suitable for object creation"""
        kwargs = {}
        kwargs['parent'] = self.container
        kwargs['name'] = self._name
        kwargs['type'] = self._typei
        kwargs['access'] = self._access
        kwargs['static'] = self._static
        kwargs['virtual'] = self._virtual
        kwargs['pure'] = self._pure
        kwargs['inline'] = self._inline
        kwargs['template'] = self._template
        kwargs['template_types'] = self._template_types
        kwargs['note'] = self._note
        kwargs['declare'] = self._declare
        kwargs['implement'] = self._implement
        return kwargs

    def CopyAttributes(self, method):
        """Copy attributes to method"""
        method._name = self._name
        method._typei = copy.copy(self._typei)
        method._access = self._access
        method._static = self._static
        method._virtual = self._virtual
        method._pure = self._pure
        method._inline = self._inline
        method._const_method = self._const_method
        method.note = self._note
        method._template = self._template
        method._template_types = self._template_types
        method._declare = self._declare
        method._implement = self._implement

    def SetAttributes(self, method):
        """Setup attributes for editing already method"""
        self.m_comboBox5.SetValue(method._name)
        iSel = self.m_choice2.FindString(method._access)
        self.m_choice2.SetSelection(iSel)
        self.m_checkBox6.SetValue(method._static)
        self.m_checkBox11.SetValue(method._virtual)
        self.m_checkBox21.SetValue(method._pure)
        self.m_checkBox31.SetValue(method._inline)
        self.m_checkBox41.SetValue(method._const_method)
        self.m_richText1.SetValue(method._note)
        self.SetTitle("Edit method")
        if method._template is not None:
            self.m_checkBox63.SetValue(True)
            self.m_stStartTemplate.Enable(True)
            self.m_template.Enable(True)
            self.m_stEndTemplate.Enable(True)
            self.m_template.SetValue(method._template)
            # if template is specified and the method holds arguments
            # using that types, the template specification cannot be changed
            for arg in method[model.cc.Argument]:
                if arg._typei._type_alias in method._template_types:
                    self.m_checkBox63.Enable(False)
                    self.m_checkBox63.SetToolTipString(
                        'Template cannot be edited because arguments using template types exist.')
                    self.m_stStartTemplate.Enable(False)
                    self.m_template.Enable(False)
                    self.m_stEndTemplate.Enable(False)
                    break
        ti = method._typei
        iSel = self.m_choice1.FindString(ti.type_name)
        self.m_choice1.SetSelection(iSel)
        self.m_checkBox1.SetValue(ti._const)
        self.m_checkBox3.SetValue(ti._ptr)
        self.m_checkBox2.SetValue(ti._ref)
        self.m_checkBox4.SetValue(ti._ptr_to_ptr)
        self.m_checkBox5.SetValue(ti._const_ptr)
        if ti._type_args is not None:
            self.m_staticText65.Enable(True)
            self.m_template_args.Enable(True)
            self.m_staticText66.Enable(True)
            self.m_template_args.SetValue(ti._type_args)
        self.m_checkBox85.SetValue(method._declare)
        self.m_checkBox86.SetValue(method._implement)

    def OnPointerToggle(self, event):
        """ptr toggle gui"""
        if self.m_checkBox3.IsChecked():
            self.m_checkBox4.Enable(True)
            self.m_checkBox5.Enable(True)
        else:
            self.m_checkBox4.SetValue(False)
            self.m_checkBox5.SetValue(False)
            self.m_checkBox4.Enable(False)
            self.m_checkBox5.Enable(False)
        event.Skip()

    def OnKeyDown(self, event):
        """Listbox selection"""
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_UP or keycode == wx.WXK_NUMPAD_UP:
            i = self.m_choice1.GetSelection()
            if i is not wx.NOT_FOUND and i > 0:
                self.m_choice1.SetSelection(i - 1)
        elif keycode == wx.WXK_DOWN or keycode == wx.WXK_NUMPAD_DOWN:
            i = self.m_choice1.GetSelection() + 1
            if i > wx.NOT_FOUND and i < len(self._types):
                self.m_choice1.SetSelection(i)
        elif keycode < 256:
            keychar = chr(keycode)
            if keychar.isalnum() or keycode is wx.WXK_SPACE:
                self.choiceStr += keychar.lower()
                for t in self._types:
                    tl = t.lower()
                    if tl.find(self.choiceStr) == 0:
                        sel = self.m_choice1.FindString(t)
                        if sel is not wx.NOT_FOUND:
                            self.m_choice1.SetSelection(sel)
                            if keycode is not wx.WXK_SPACE:
                                event.Skip()
                            return
            self.choiceStr = ""
        event.Skip()

    # Handlers for NewMethod events.
    def OnCancel(self, event):
        """cancel event handler"""
        self.EndModal(wx.ID_CANCEL)

    def OnOK(self, event):
        """ok event handler"""
        if self.Validate():
            self.EndModal(wx.ID_OK)


