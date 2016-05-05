from tran import TransactionStack


class TransactionObject(object):
    """This class constitutes the base for transaction objects, i.e.
    objects that can be created and deleted with stack recording"""
    def __init__(self, *args, **kwargs):
        TransactionStack.DoCreate(self)

    def RemoveRelations(self):
        pass

    def RestoreRelations(self):
        pass

    def OnUndoRedoRemoving(self):
        pass

    def OnUndoRedoAdd(self):
        pass

    def OnUndoRedoChanged(self):
        pass

    def InUndoRedo(self):
        return TransactionStack.InUndoRedo()

    def InUndo(self):
        return TransactionStack.InUndo()

    def InRedo(self):
        return TransactionStack.InRedo()

    def SaveState(self):
        TransactionStack.DoSaveState(self)

    def Delete(self):
        """Do a transactional delete for any object"""
        TransactionStack.DoDelete(self)

    def Dispose(self):
        """When an object is finally removed from the stack,
        the associated external resources may be also released."""
        pass