# -*- coding: utf-8 -*-
import wx
from ctx import localcontext as context



class CreationDialog(object):
    """Class decorator for creation dialog. With this decorator
    the decorated method only needs to send the dialog arguments"""
    def __init__(self, dialogType, objectType):
        """"""
        self._dialogType = dialogType
        self._objectType = objectType

    def __call__(self, method):
        """"""
        import tran.TransactionStack as stack

        def wrapped_call(*args, **kwargs):
            """Code dialog creation"""
            dialog = self._dialogType(*method(*args, **kwargs))
            rtv = dialog.ShowModal()
            if rtv != wx.ID_OK:
                return False
            kw_or_kwlargs = dialog.get_kwargs()
            #si kw_or_kwlargs es None, no se ha de hacer nada
            if kw_or_kwlargs:
                # si kw_or_kwlargs es una lista, se interpreta que se han de crear
                # multiples objetos y se trata de una lista de kwargs
                if type(kw_or_kwlargs) is list:
                    for kwargs in kw_or_kwlargs:
                        self._objectType(**kwargs)
                else:
                    obj = self._objectType(**kw_or_kwlargs)
                    # give the possibility of insert object name in transaction label
                    if obj and stack.InTransaction() and hasattr(obj, '_name'):
                        sname = stack.instance.GetName()
                        if sname:
                            sname = sname.format(obj._name)
                            stack.instance.SetName(sname)
            return True
        return wrapped_call


class CreationDialogEx(object):
    """Class decorator for creation dialog with multilanguage support.
    The dialog and the object type for, is returned by the method"""
    def __init__(self):
        """"""
        super(CreationDialogEx, self).__init__()

    def __call__(self, method):
        """"""
        def wrapped_call(*args, **kwargs):
            """Code dialog creation"""
            args = method(*args, **kwargs)
            self._dialogType = args[0]
            self._objectType = args[1]
            args = args[2:]
            dialog = self._dialogType(*args)
            if dialog.ShowModal() != wx.ID_OK:
                return False
            kw_or_kwlargs = dialog.get_kwargs()
            #si kw_or_kwlargs es None, no se ha de hacer nada
            if kw_or_kwlargs:
                # si kw_or_kwlargs es una lista, se interpreta que se han de crear
                # multiples objetos y se trata de una lista de kwargs
                if type(kw_or_kwlargs) is list:
                    for kwargs in kw_or_kwlargs:
                        self._objectType(**kwargs)
                else:
                    obj = self._objectType(**kw_or_kwlargs)
                    # give the possibility of insert object name in transaction label
                    if obj and stack.InTransaction() and hasattr(obj, '_name'):
                        sname = stack.instance.GetName()
                        if sname:
                            sname = sname.format(obj._name)
                            stack.instance.SetName(sname)
            return True
        return wrapped_call