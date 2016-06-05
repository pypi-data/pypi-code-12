# -*- coding: utf-8 -*-

"""This represents a pending task.
The task uses glass_clock as tree icon"""

import wx
import model
import tran
import app.resources as rc


class Task(model.TComponent):
    """Declares the task element"""
    task_container = True  # allow subtasks

    #visual methods
    @tran.TransactionalMethod('move task {}')
    def drop(self, to):
        """drop this elemento to another place"""
        target = to.inner_task_container
        if not target or to.project != self.project:
            return False  # avoid move arguments between projects
        index = 0
        new_cont = target.status_container
        if new_cont is not self.status_container:
            new_cont.SetStatus(self)
        tran.TransactionalMoveObject(
            object=self, origin=self.parent, target=target, index=index)
        return True

    @property
    def status_container(self):
        """return the status container"""
        return self.parent.status_container

    """Declares a task entry"""
    def __init__(self, **kwargs):
        """Constructor"""
        self._status = kwargs.get('status', 'pending')
        self._priority = kwargs.get('priority', 'normal')
        self._taskType = kwargs.get('type', 'CHANGE')
        self._reference = kwargs.get('reference', 'None')
        self._dateCreated = kwargs.get('dateCreated', 'None')
        self._dateBegin = kwargs.get('dateBegin', 'None')
        self._dateEnd = kwargs.get('dateEnd', '')
        super(Task, self).__init__(**kwargs)

    def get_kwargs(self):
        """Get the info about the class"""
        kwargs = {
            'status': self._status,
            'priority': self._priority,
            'type': self._taskType,
            'reference': self._reference,
            'dateCreated': self._dateCreated,
            'dateBegin': self._dateBegin,
            'dateEnd': self._dateEnd
            }
        kwargs.update(super(Task, self).get_kwargs())
        return kwargs

    #backward-compatibility
    def __setstate__(self, d):
        """Add the creation field if missing"""
        if '_dateCreated' not in d:
            d['_dateCreated'] = wx.DateTime.Now().Format('%Y-%m-%d %H:%M:%S')
        self.__dict__ = d

    @property
    def bitmap_index(self):
        """Index of tree image"""
        return rc.GetBitmapIndex('glass_clock')
