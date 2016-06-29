"""Transaction stack definition"""
import copy


def copy_temps(obj):
    """Copy with temps"""
    s = copy.copy(obj)
    state = dict(obj.__dict__)
    if '_pane' in state:
        s._pane = obj._pane
    if '_paneIndex' in state:
        s._paneIndex = obj._paneIndex
    if '_parentIndex' in state:
        s._parentIndex = obj._parentIndex
    if '_elements' in state:
        s._elements = copy.copy(obj._elements)
    if '_ancestors' in state:
        s._ancestors = copy.copy(obj._ancestors)
    if '_derivatives ' in state:
        s._derivatives = copy.copy(obj._derivatives)
    if '_fromRelation ' in state:
        s._fromRelation = copy.copy(obj._fromRelation)
    if '_toRelation ' in state:
        s._toRelation = copy.copy(obj._toRelation)
    if '_contexts' in state:
        s._contexts = copy.copy(obj._contexts)
    return s


def respect_visuals_from(oldobj, newobj):
    """Respect visual changes"""
    state = dict(oldobj.__dict__)
    if '_pane' in state:
        newobj._pane = oldobj._pane
    else:
        newobj._pane = None


class Transaction(object):
    """Implements a single transaction"""
    def __init__(self, name):
        """Initialice transaction"""
        self._key = None
        self._name = name
        self._operations = []

    def Dispose(self):
        """Notify all transaction componentes that it will be"""
        for op in self._operations:
            op.Dispose()

    @property
    def key(self):
        """return the key"""
        return self._key

    def SetKey(self, key):
        """sets the key"""
        self._key = key

    def Rollback(self):
        """Rollback transaction"""
        while len(self._operations) > 0:
            self._operations.pop().Rollback()

    def Undo(self):
        """Undoes transaction"""
        redo_operations = []
        while len(self._operations) > 0:
            redo_operations.append(self._operations.pop().Undo())
        self._operations = redo_operations
        return self

    def Redo(self):
        """Redoes transaction"""
        undo_operations = []
        while len(self._operations) > 0:
            undo_operations.append(self._operations.pop().Redo())
        self._operations = undo_operations
        return self

    def RefreshChanges(self):
        """Ensures visual update of saved states"""
        for operation in self._operations:
            if type(operation) is UndoChange:
                operation._obj.OnUndoRedoChanged()


class UndoLoad(object):
    """Implements a undo load operation"""
    def __init__(self, obj):
        """Init"""
        obj.OnUndoRedoLoaded()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        pass

    def Rollback(self):
        """Implements rollback"""
        self._obj.OnUndoRedoUnloaded()
        self._obj.RemoveRelations()

    def Undo(self):
        """Implements undo"""
        return RedoLoad(self._obj)


class UndoUnload(object):
    """Implements a undo unload operation"""
    def __init__(self, obj):
        """Init"""
        obj.OnUndoRedoUnloaded()
        obj.RemoveRelations()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        pass

    def Rollback(self):
        """Implements rollback"""
        self._obj.RestoreRelations()
        self._obj.OnUndoRedoLoaded()

    def Undo(self):
        """Implements undo"""
        return RedoUnload(self._obj)


class RedoLoad(object):
    """Implements a redo for load operation"""
    def __init__(self, obj):
        """Initialize redo"""
        obj.OnUndoRedoUnloaded()
        obj.RemoveRelations()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        del self._obj  # unloaded objects dont interact

    def Redo(self):
        """Implements redo"""
        self._obj.RestoreRelations()
        return UndoLoad(self._obj)


class RedoUnload(object):
    """Implements a redo unload operation"""
    def __init__(self, obj):
        """Init"""
        obj.RestoreRelations()
        obj.OnUndoRedoLoaded()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        del self._obj  # unloaded objects dont interact
        pass

    def Undo(self):
        """Implements undo"""
        return UndoUnload(self._obj)

class UndoNew(object):
    """Implements a undo new operation"""
    def __init__(self, obj):
        """Init"""
        obj.OnUndoRedoAdd()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        pass

    def Rollback(self):
        """Implements rollback"""
        self._obj.OnUndoRedoRemoving()
        self._obj.RemoveRelations()

    def Undo(self):
        """Implements undo"""
        return RedoNew(self._obj)

class RedoNew(object):
    """Implements a redo new operation"""
    def __init__(self, obj):
        """Initialize redo"""
        obj.OnUndoRedoRemoving()
        obj.RemoveRelations()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        self._obj.Dispose()

    def Redo(self):
        """Implements redo"""
        self._obj.RestoreRelations()
        return UndoNew(self._obj)

class UndoDelete(object):
    """Implements a undo delete operation"""
    def __init__(self, obj):
        """Initialize undo"""
        obj.OnUndoRedoRemoving()
        obj.RemoveRelations()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        self._obj.Dispose()

    def Rollback(self):
        """Implements rollback"""
        self._obj.RestoreRelations()
        self._obj.OnUndoRedoAdd()

    def Undo(self):
        """Implements undo"""
        return RedoDelete(self._obj)


class RedoDelete(object):
    """Implements a redo delete operation"""
    def __init__(self, obj):
        """Initialize redo"""
        obj.RestoreRelations()
        obj.OnUndoRedoAdd()
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        pass

    def Redo(self):
        """Implements redo"""
        return UndoDelete(self._obj)


class UndoChange(object):
    """Implements a undo change operation"""
    def __init__(self, obj):
        """Initialize undo change"""
        self._oldObj = copy_temps(obj)
        self._obj = obj

    def Dispose(self):
        """Remove associated data"""
        self._oldObj.Dispose()

    def Rollback(self):
        """Implements rollback"""
        self._obj.RemoveRelations()
        self._obj .__dict__ = self._oldObj.__dict__.copy()
        self._obj.RestoreRelations()
        self._obj.OnUndoRedoChanged()

    def Undo(self):
        """Implements undo"""
        return RedoChange(self._oldObj, self._obj)


class RedoChange(object):
    """Implements a redo change operation"""
    def __init__(self, oldObj, obj):
        """Initialize redo change"""
        self._newObj = copy_temps(obj)
        self._obj = obj
        self._obj.RemoveRelations()
        self._obj .__dict__ = oldObj.__dict__.copy()
        respect_visuals_from(self._newObj, self._obj)
        self._obj.RestoreRelations()
        self._obj.OnUndoRedoChanged()

    def Dispose(self):
        """Remove associated data"""
        self._newObj.Dispose()

    def Redo(self):
        """Implements redo"""
        r = UndoChange(self._obj)
        self._obj.RemoveRelations()
        self._obj .__dict__ = self._newObj.__dict__.copy()
        self._obj.RestoreRelations()
        self._obj.OnUndoRedoChanged()
        return r


class TransactionStack(object):
    """Implements a queue of stacked operations"""
    instance = None
    delayedCalls = {}
    delayedCallsFiltered = []

    @staticmethod
    def DoBeginTransaction(name=None):
        """Starts a new transaction"""
        TransactionStack.instance.BeginTransaction(name)

    @staticmethod
    def DoCommit():
        """Commit transaction"""
        TransactionStack.instance.Commit()

    @staticmethod
    def DoRollback():
        """Rollback transaction"""
        TransactionStack.instance.Rollback()

    @staticmethod
    def DoUndo():
        """Rollback transaction"""
        TransactionStack.instance.Undo()

    @staticmethod
    def DoRedo():
        """Rollback transaction"""
        TransactionStack.instance.Redo()

    @staticmethod
    def DoCreate(obj):
        """Create transaction"""
        TransactionStack.instance.Create(obj)

    @staticmethod
    def DoLoad(obj):
        """Load transaction"""
        TransactionStack.instance.Load(obj)

    @staticmethod
    def DoUnload(obj):
        """Unload transaction"""
        TransactionStack.instance.Unload(obj)

    @staticmethod
    def DoDelete(obj):
        """Create transaction"""
        TransactionStack.instance.Delete(obj)

    @staticmethod
    def DoSaveState(obj):
        """Save object state"""
        TransactionStack.instance.SaveState(obj)

    @staticmethod
    def InTransaction():
        """Returns info about undo/redo"""
        return TransactionStack.instance._tran is not None

    @staticmethod
    def InUndoRedo():
        """Returns info about undo/redo"""
        return TransactionStack.instance._inUndoRedo

    @staticmethod
    def InUndo():
        """Returns info about undo/redo"""
        return TransactionStack.instance._inUndo

    @staticmethod
    def InRedo():
        """Returns info about undo/redo"""
        return TransactionStack.instance._inRedo

    @staticmethod
    def DoSetKey(key):
        """Set the key for the current, uncommited transaction"""
        return TransactionStack.instance.SetKey(key)

    def __init__(self, deep):
        """Initialize the transaction stack"""
        self._deep = deep
        self._undo = []
        self._redo = []
        self._tran = None
        self._inUndoRedo = False
        self._inRedo = False
        self._inUndo = False
        self._logger = None
        TransactionStack.instance = self

    def TransactionStatus(self, hashcode):
        """This method is a facility for loggers to see the
        current status of some log entry. The return code
        will be:
            1 ... transaction exists in the redo stack
            0 ... transaction exists in the undo stack
           -1 ... transaction don't exist anymore (may be deleted from some stack)'"""
        if hashcode in (hash(tran) for tran in self._redo):
            return 1
        if hashcode in (hash(tran) for tran in self._undo):
            return 0
        return -1

    def SetLogger(self, logger):
        """Set an method logger that will be called for:

            a) Each new transaction commit
            b) Each new transaction undo
            c) Each new transaction redo

            The logger will receive the transaction
            and a text mode 'commit', 'undo' or 'redo'.
            Indeed, the logger will receive 'start'
            and 'end' messages (without transaction)
            for the SetLogger and for SetLogger(None).
            logger = fn(command, transaction=None)

            The obvious mission : create logs for projects
            and/or workspace
        """
        if self._logger == logger:
            # stupid call will be dissmissed
            return
        # finalize previous loggers
        if self._logger:
            self._logger('end')

        self._logger = logger
        # start new transaction logger
        if self._logger:
            self._logger('start')

    def BeginTransaction(self, name=''):
        """Starts a new transaction"""
        if self._tran is None:
            self._tran = Transaction(name)
            self._inTran = True
        return self._tran

    def Commit(self):
        """Commit an open transaction"""
        if self._tran is None:
            return
        self._inUndoRedo = False
        self._inRedo = False
        self._inUndo = False
        self._tran.RefreshChanges()
        self._undo.append(self._tran)
        if self._logger:
            self._logger('commit', transaction=self._tran)
        self._tran = None
        self.CleanRedo()
        for method in TransactionStack.delayedCalls:
            if method in TransactionStack.delayedCallsFiltered:
                continue
            for l in TransactionStack.delayedCalls[method]:
                method(*l[0], **l[1])
        TransactionStack.delayedCalls = {}
        TransactionStack.delayedCallsFiltered = []
        while len(self._undo) > self._deep:
            self._undo[0].Dispose()
            del self._undo[0]

    def Rollback(self):
        """Rollback an open transaction"""
        if self._tran is None:
            return
        self._inUndoRedo = True
        self._tran.Rollback()
        TransactionStack.delayedCalls = {}
        TransactionStack.delayedCallsFiltered = []
        self._tran = None
        self._inUndoRedo = False

    def Undo(self):
        """Undoes the last operation"""
        self._inUndoRedo = True
        self._inUndo = True
        if not self._tran is None:
            self.Rollback()
        elif len(self._undo) > 0:
            if self._logger:
                self._logger('undo')
            self._redo.append(self._undo.pop().Undo())
        self._inUndoRedo = False
        self._inUndo = False
        while TransactionStack.delayedCalls:
            k = TransactionStack.delayedCalls[0]
            k[0](*k[1], **k[2])
            del TransactionStack.delayedCalls[0]
        TransactionStack.delayedCallsFiltered = []

    def Redo(self):
        """Redoes the last operation"""
        self._inUndoRedo = True
        self._inRedo = True
        if not self._tran is None:
            self.Rollback()
        if len(self._redo) > 0:
            if self._logger:
                self._logger('redo')
            self._undo.append(self._redo.pop().Redo())
        self._inUndoRedo = False
        self._inRedo = False
        while TransactionStack.delayedCalls:
            k = TransactionStack.delayedCalls[0]
            k[0](*k[1], **k[2])
            del TransactionStack.delayedCalls[0]
        TransactionStack.delayedCallsFiltered = []

    def CanRedo(self):
        """Check about redo availability"""
        return len(self._redo) > 0

    def CanUndo(self):
        """Check about undo availability"""
        return len(self._undo) > 0

    def CleanRedo(self):
        """Clean redo stack"""
        for k in self._redo:
            k.Dispose()
        self._redo = []

    def CleanUndo(self):
        """Clean undo stack"""
        for k in self._undo:
            k.Dispose()
        self._undo = []

    def UndoName(self):
        """Get undo name"""
        if len(self._undo) > 0:
            return self._undo[-1]._name
        return None

    def SetKey(self, key):
        """Sets the key for the current, uncommited transaction"""
        if self._tran:
            self._tran.SetKey(key)
            return True
        return False

    def GetName(self):
        """Get the current, uncommited transaction name"""
        if self._tran:
            return self._tran._name
        return None

    def SetName(self, name):
        """Set the current, uncommited transaction name"""
        if self._tran:
            self._tran._name = name
        return None

    def RedoName(self):
        """Get redo name"""
        if len(self._redo) > 0:
            return self._redo[-1]._name

    def SaveState(self, obj):
        """Save object state"""
        if self._tran is None:
            self.BeginTransaction()
        if not self.SavedState(obj):
            # some operations can trigger others so we must ensure order
            pos = len(self._tran._operations)
            self._tran._operations.insert(pos, UndoChange(obj))

    def SavedState(self, obj):
        """Checks about saved state"""
        if self._tran is None:
            return False
        for operation in self._tran._operations:
            if type(operation) is UndoChange:
                if operation._obj == obj:
                    return True
        return False

    def Delete(self, obj):
        """Delete object"""
        if self._tran is None:
            self.BeginTransaction()
        # some operations can trigger others so we must ensure order
        pos = len(self._tran._operations)
        self._tran._operations.insert(pos, UndoDelete(obj))

    def Create(self, obj):
        """Create object"""
        if self._tran is None:
            self.BeginTransaction()
            try:
                pos = len(self._tran._operations)
                self._tran._operations.insert(pos, UndoNew(obj))
                self.Commit()
            except:
                self.Rollback()
        else:
            # some operations can trigger others so we must ensure order
            pos = len(self._tran._operations)
            self._tran._operations.insert(pos, UndoNew(obj))

    def Load(self, obj):
        """Load object"""
        if self._tran is None:
            self.BeginTransaction()
        # some operations can trigger others so we must ensure order
        pos = len(self._tran._operations)
        self._tran._operations.insert(pos, UndoLoad(obj))

    def Unload(self, obj):
        """Unload object"""
        if self._tran is None:
            self.BeginTransaction()
        # some operations can trigger others so we must ensure order
        pos = len(self._tran._operations)
        self._tran._operations.insert(pos, UndoUnload(obj))

