# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-

"""
This class allows to set some common handlers and methods for
easy view declaration"""

import wx
import wxx
import tran
import app
import model
from ctx import localcontext as context


class BasePane(object):
    """Declares a base pane class"""

    def __init__(self, *args, **kwargs):
        """Initialize base view"""
        self._evtHandler = wx.PyEvtHandler()
        self._handler_installed = False
        self._focus = False
        super(BasePane, self).__init__(*args, **kwargs)

    def BindSpecial(self, evtID, handler, source=None, id=-1, id2=-1):
        """Do a special binding for pluggable event handler and also internal event handler"""
        self._evtHandler.Bind(evtID, handler, source=source, id=id, id2=id2)
        self.Bind(evtID, handler, source=source, id=id, id2=id2)

    def install_handler(self):
        """Installs the event handler"""
        if self._handler_installed:
            return False  # already installed
        context.frame.PushEventHandler(self._evtHandler)
        self._handler_installed = True
        return True  # ok, installed

    def remove_handler(self):
        """Remove the event handler"""
        if not self._handler_installed:
            return False  # already removed
        # pop event handlers until found this
        other_event_handlers = []
        evth = context.frame.PopEventHandler()
        try:
            while evth != self._evtHandler:
                other_event_handlers.append(evth)
                evth = context.frame.PopEventHandler()
            if evth == self._evtHandler:
                self._handler_installed = False
            result = True
        except:
            print "Fatal error : missing event handler"
            self._handler_installed = False
            result = False
        # reinstall the event handlers chain
        while len(other_event_handlers):
            context.frame.PushEventHandler(other_event_handlers.pop())
        return result

    @property
    def is_event_handler(self):
        """return info about if the handler is installed"""
        return self._handler_installed

    def PreDelete(self):
        """Remove the event handler"""
        self.remove_handler()

    def NotifyShow(self):
        """Called where the git view is show"""
        self.install_handler()

    def NotifyHide(self):
        """Called where the git view is hidden"""
        self.remove_handler()


