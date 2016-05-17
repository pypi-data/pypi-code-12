
import mirpyidl
from mirpyidl import setLoggingLevel, InitializeIdlrpc, CleanupIdlrpc

# ==============================================================================
# ==============================================================================
# Define module level convenience functions.
def callFunction(*args, **kwargs):
    idl = PyIDL()
    return idl.callFunction(*args, **kwargs)

def callPro(*args, **kwargs):
    idl = PyIDL()
    return idl.callPro(*args, **kwargs)

def execute(*args):
    idl = PyIDL()
    idl.execute(*args)

def setVariable(*args):
    idl = PyIDL()
    idl.setVariable(*args)

def getVariable(*args):
    idl = PyIDL()
    return idl.getVariable(*args)

def ex(*args):
    idl = PyIDL()
    idl.execute(*args)

def set(*args):
    idl = PyIDL()
    idl.setVariable(*args)

def get(*args):
    idl = PyIDL()
    return idl.getVariable(*args)


# ==============================================================================
# ==============================================================================
# Define IDLRPC version of PyIDL within this module.
class PyIDL(mirpyidl.PyIDL):

    def __init__(self):
         super(PyIDL, self).__init__(use_idlrpc=True)
         
class PyIDLObject(mirpyidl.PyIDLObject):
    
    def _getPyIDL(self):
        """Return the PyIDL object. This is separated to simplify sublcassing."""
        return PyIDL()
