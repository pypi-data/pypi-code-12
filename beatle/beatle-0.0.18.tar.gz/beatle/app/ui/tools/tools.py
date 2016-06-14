# -*- coding: utf-8 -*-
import wx
import wxx
import tran
import model
from app.ui import dlg
from activity.models.ui import dlg as mdlg

edit_dict = {
        model.Workspace: (dlg.WorkspaceDialog, 'edit workspace {}'),
        model.cc.Namespace: (mdlg.NamespaceDialog, 'edit namespace {}'),
        model.cc.Type: (mdlg.TypeDialog, 'edit type {}'),
        model.cc.Class: (mdlg.ClassDialog, 'edit c++ class {}'),
        model.py.Class: (mdlg.PyClassDialog, 'edit python class {}'),
        model.cc.Argument: (mdlg.ArgumentDialog, 'edit c++ method argument {}'),
        model.py.Argument: (mdlg.PyArgumentDialog, 'edit python method argument {}'),
        model.Folder: (dlg.FolderDialog, 'edit folder {}'),
        model.ClassDiagram: (mdlg.ClassDiagramDialog, 'edit class diagram {}'),
        model.cc.Inheritance: (mdlg.InheritanceDialog, 'edit c++ inheritance {}'),
        model.py.Inheritance: (mdlg.PyInheritanceDialog, 'edit python inheritance {}'),
        model.cc.MemberData: (mdlg.MemberDialog, 'edit c++ class member {}'),
        model.py.MemberData: (mdlg.PyMemberDialog, 'edit python class member {}'),
        model.cc.Data: (mdlg.VariableDialog, 'edit c++ variable {}'),
        model.py.Data: (mdlg.PyVariableDialog, 'edit python variable {}'),
        model.cc.Constructor: (mdlg.ConstructorDialog, 'edit c++ {} constructor'),
        model.py.InitMethod: (mdlg.PyMemberMethodDialog, 'edit python __init__ method'),
        model.cc.MemberMethod: (mdlg.MemberMethodDialog, 'edit c++ method {}'),
        model.py.MemberMethod: (mdlg.PyMemberMethodDialog, 'edit python method {}'),
        model.cc.IsClassMethod: (mdlg.MemberMethodDialog, 'edit c++ method {}'),
        model.cc.Destructor: (mdlg.DestructorDialog, 'edit c++ destructor {}'),
        model.cc.Module: (mdlg.ModuleDialog, 'edit c++ module "{}"'),
        model.cc.Function: (mdlg.FunctionDialog, 'edit c++ function {}'),
        model.py.Function: (mdlg.PyFunctionDialog, 'edit python function {}'),
        model.Note: (mdlg.NoteDialog, 'edit note'),
        model.cc.Enum: (mdlg.EnumDialog, 'edit c++ enum {}'),
        model.Project: (mdlg.ProjectDialog, 'edit project {}'),
        model.cc.RelationFrom: (mdlg.RelationDialog, 'edit relation'),
        model.cc.RelationTo: (mdlg.RelationDialog, 'edit relation'),
        model.py.Module: (mdlg.PyModuleDialog, 'edit python module {}'),
        model.py.Import: (mdlg.PyImportDialog, 'edit python import {}'),
        model.py.Decorator: (mdlg.PyDecoratorDialog, 'edit python decorator {}'),
        model.cc.pyBoostModule: (mdlg.BoostPythonModuleDialog, 'edit boost.python module {}'),
    }


def edit(parent, obj):
    """Edit the object"""
    t = type(obj)
    if t in edit_dict:
        v = edit_dict[t]

        @tran.TransactionalMethod(v[1])
        @wxx.EditionDialog(v[0])
        def editDialog(parent, obj):
            """Handle type edition"""
            return (parent, obj)

        editDialog(parent, obj)
        return True
    return False


def append_menuitem_copy(menu, menuitem):
    """Add a menuitem clone"""
    clone = wx.MenuItem(menu, menuitem.GetId(), menuitem.GetText(), menuitem.GetHelp(), menuitem.GetKind())
    if menuitem.GetBitmap().IsOk():
        clone.SetBitmap(menuitem.GetBitmap())
    menu.AppendItem(clone)
    if menuitem.GetKind() is wx.ITEM_CHECK:
        clone.Check(menuitem.IsChecked())


def set_menu_handlers(frame, imnu, command, update):
    """This method travels through the whole menu
    and submenu structure and set dispatch handlers.
    This method is used for dispatching events to focused
    windows that install the menus"""
    if type(imnu) is wx.Menu:
        for x in imnu.GetMenuItems():
            set_menu_handlers(frame, x, command, update)
    if type(imnu) is wx.MenuItem:
        frame.Bind(wx.EVT_MENU, command, id=imnu.GetId())
        frame.Bind(wx.EVT_UPDATE_UI, update, id=imnu.GetId())


def unset_menu_handlers(frame, imnu, command, update):
    """This method travels through the whole menu
    and submenu structure and unset dispatch handlers.
    This method is used for dispatching events to focused
    windows that install the menus"""
    if type(imnu) is wx.Menu:
        for x in imnu.GetMenuItems():
            set_menu_handlers(frame, x, command, update)
    if type(imnu) is wx.MenuItem:
        frame.Unbind(wx.EVT_MENU, command, id=imnu.GetId())
        frame.Unbind(wx.EVT_UPDATE_UI, update, id=imnu.GetId())


def clone_mnu(imnu, parent=None, enabled=False, notitle=False, separator=False):
    """
    Clone a menu or menuitem recursively. If
    enabled is specified, disabled items are filtered.
    separator makes sense only when parent is not None.
    This case, an separator will be added before the first
    menuitem to be copied.
    """
    if type(imnu) is wx.Menu:
        # if we filter disabled elements, we need to update menu first
        if enabled:
            imnu.UpdateUI()
        # if parent is specified the menu items are copied
        # if not, new menu is created
        if parent:
            clone = parent
            if separator:
                pos = clone.GetMenuItemCount()
        else:
            title = (not notitle and imnu.GetTitle()) or wx.EmptyString
            style = imnu.GetStyle()
            separator = False
            clone = wx.Menu(title=title, style=style)
        subs = [clone_mnu(x, clone, enabled) for x in
            imnu.GetMenuItems() if not enabled or x.IsEnabled()]
        subs = [x for x in subs if x is not None]
        if len(subs) > 0:
            # remove begin/adjoint/end separators
            while len(subs) and subs[0].GetKind() == wx.ITEM_SEPARATOR:
                clone.DestroyItem(subs[0])
                del subs[0]
            while len(subs) and subs[-1].GetKind() == wx.ITEM_SEPARATOR:
                clone.DestroyItem(subs[-1])
                del subs[-1]
            for i in range(len(subs) - 1, -1, -1):
                # remove duplicated separators
                if subs[i].GetKind() != wx.ITEM_SEPARATOR:
                    continue
                if subs[i - 1].GetKind() != wx.ITEM_SEPARATOR:
                    continue
                clone.DestroyItem(subs[i])
                del subs[i]
            if len(subs) > 0:
                if separator:
                    clone.InsertSeparator(pos)
                return clone
        if not parent:
            del clone
        return None
    if type(imnu) is wx.MenuItem:
        if enabled and not imnu.IsEnabled():
            return None
        simnu = imnu.GetSubMenu()
        if simnu is not None:
            simnu = clone_mnu(simnu, None, enabled)
        clone = wx.MenuItem(parent, imnu.GetId(), imnu.GetText(), imnu.GetHelp(), imnu.GetKind(), simnu)
        if imnu.GetBitmap().IsOk():
            clone.SetBitmap(imnu.GetBitmap())
        if parent is not None:
            parent.AppendItem(clone)
        if imnu.GetKind() is wx.ITEM_CHECK:
            clone.Check(imnu.IsChecked())
        return clone
