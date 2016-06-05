# -*- coding: utf-8 -*-
import tran


class TransactionalMoveObject(tran.TransactionObject):
    """Implements a relationship move operation"""
    def __init__(self, **kwargs):
        """Initialice move"""
        self._object = kwargs['object']
        self._origin = kwargs['origin']
        self._target = kwargs['target']
        self._target_index = kwargs.get('index', 0)
        super(TransactionalMoveObject, self).__init__()
        #if the object has name, give the opportunity to add this name
        #to the current transaction name, so it will be visible in menu
        #take in amodelount that not format will remains after that, so
        #nested transactions will no see his object names included, if any
        if hasattr(self._object, '_name'):
            sname = tran.TransactionStack.instance.GetName()
            if sname:
                sname = sname.format(self._object._name)
                tran.TransactionStack.instance.SetName(sname)

    def OnUndoRedoAdd(self):
        """Process on undo redo add"""
        self._object.OnUndoRedoRemoving()  # this is a hack specific for move object
        self._object.RemoveRelations()
        self._object._parent = self._target
        if hasattr(self._object, '_parentIndex'):
            self._origin_index = self._object._parentIndex
        self._object._parentIndex = self._target_index
        self._object.RestoreRelations()
        self._object.OnUndoRedoAdd()
        super(TransactionalMoveObject, self).OnUndoRedoAdd()

    def OnUndoRedoRemoving(self):
        """Process on undo redo removed"""
        self._object.OnUndoRedoRemoving()
        self._object.RemoveRelations()
        self._object._parent = self._origin
        if hasattr(self, '_origin_index'):
            self._object._parentIndex = self._origin_index
        elif hasattr(self._object, '_parentIndex'):
            del self._object._parentIndex
        self._object.RestoreRelations()
        self._object.OnUndoRedoAdd()
        super(TransactionalMoveObject, self).OnUndoRedoAdd()


