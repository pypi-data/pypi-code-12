import pykd
import re
import pkgutil
import types
from abc import abstractmethod

def getLocalsCount():

    try:
        return len(pykd.getFrame().getParams() + pykd.getFrame().getLocals())
    except pykd.DbgException:
        return 0


def getLocal(localIndex,subitems):

    try:

        varName, var = (pykd.getFrame().getParams() + pykd.getFrame().getLocals())[localIndex]

        varPrinter = getMultilinePrinter(varName, var)

        for subitem in subitems:
            varPrinter = varPrinter.getSubPrinter(subitem)

        return (varPrinter.getVarName(), varPrinter.getVarType(), varPrinter.getVarLocation(), varPrinter.getVarShortValue(), varPrinter.getVarSubitems() )

    except pykd.DbgException as e:
       
        return ( str(localIndex), "", "", "", "" )

def getTypedVar(varName, subitems):

    try:

        var = pykd.typedVar(varName)
        varPrinter = getMultilinePrinter(varName, var)

        for subitem in subitems:
            varPrinter = varPrinter.getSubPrinter(subitem)

        return (varPrinter.getVarName(), varPrinter.getVarType(), varPrinter.getVarLocation(), varPrinter.getVarShortValue(), varPrinter.getVarSubitems() )

    except pykd.DbgException as e:
       
        return ( varName, "", "", "", "" )


def getMultilinePrinter(varName, var):

    if type(var) == pykd.typedVar:
        for multilinePrinter in multilinePrinterList:
            if re.match( multilinePrinter[0], var.type().name() ):
               return multilinePrinter[1](varName, var)
        return defaultTypedVarMultilinePrinter(varName, var)

    if type(var) == pykd.typeInfo:
        return defaultTypeInfoMultilinePrinter(varName, var)

    return pythonMultiprinter(varName, var)


def defaultTypedVarMultilinePrinter(varName, var):

    if var.type().isBase():
        return TypedVarPrinter(varName, var)

    if var.type().isUserDefined():
        return StructPrinter(varName, var)

    if var.type().isPointer():
        if var.type().deref().isUserDefined():
            return PtrStructPrinter(varName, var)
        if var.type().deref().isVtbl():
            return PtrVtblPrinter(varName, var)
        return TypedVarPrinter(varName, var)

    if var.type().isArray():
        return ArrayPrinter(varName,var)

    return TypedVarPrinter(varName, var)

def defaultTypeInfoMultilinePrinter(varName, var):
    if var.isUserDefined():
        return StructTypePrinter(varName, var)

    return TypeInfoPrinter(varName, var)

def pythonMultiprinter(varName, var):

    if isinstance(var, types.DictType):
        return DictPythonMultilinePrinter(varName, var)

    if isinstance(var, types.ListType):
        return ListPythonMultilinePrinter(varName, var)

    if isinstance(var, types.TupleType):
        return ListPythonMultilinePrinter(varName, var)

    if  isinstance(var, (types.BooleanType, types.IntType, types.LongType, types.FloatType, types.StringType, types.UnicodeType)):
        return  BasePythonMultilinePrinter(varName, var)

    return ObjPythonMultilinePrinter(varName, var)


def getShortPrinter(var):

    for shortPrinter in shortPrinterList:

        if re.match( shortPrinter[0], var.type().name() ):
            retVal = shortPrinter[1](var)
            if retVal != None:
                return retVal

    return defaultShortPrinter(var)

def defaultShortPrinter(var):

    if var.type().isBase():
        return baseVarPrinter(var)

    if var.type().isPointer():
        return pointerVarPrinter(var)

    if var.type().isArray():
        return "Array"

    if var.type().isUserDefined():
        return "Struct"

    if var.type().isEnum():
        return enumShortPrinter(var)

    if var.type().isBitField():
        return bitFieldPrinter(var)

    return var.type().name()

def baseVarPrinter(var):
    try:
        if var.isInteger():
            return str(long(var))
        else:
            return str(float(var))
    except pykd.MemoryException:
        return "access violation"

def bitFieldPrinter(var):
    try:
        return str(long(var))
    except pykd.MemoryException:
        return "access violation"

def pointerVarPrinter(var):
    try:
        return hex(var)
    except pykd.MemoryException:
        return "invalid memory (0x%x)" % var.getAddress()

def enumShortPrinter(var):
    try:
        intval = long(var)
        for i in xrange(var.type().getNumberFields()):
            if intval == var.type().field(i):
                return "%d (%s)" % ( intval, var.type().fieldName(i) )
        return "%d (no enum value match)" % intval
    except pykd.MemoryException:
        return "access violation"

class BaseMultilinePrinter(object):

    def __init__(self, varName, varValue):
        self.varName = varName
        self.varValue = varValue

    def getVarName(self):
        return self.varName

    def getVarType(self):
        return ""

    def getVarLocation(self):
        return ""

    def getVarShortValue(self):
        return ""

    def getVarSubitems(self):
        return []

    def getSubPrinter(self, subItemName):
        return None

class BasePythonMultilinePrinter(BaseMultilinePrinter):
    def __init__(self, varName, varValue):
        super(BasePythonMultilinePrinter,self).__init__(varName, varValue)

    def getVarShortValue(self):
        return repr(self.varValue)

    def getVarType(self):
        return type(self.varValue).__name__

class ObjPythonMultilinePrinter(BasePythonMultilinePrinter):

    excludeTypes = (
        types.FunctionType, types.MethodType, types.TypeType, types.BuiltinFunctionType,
        types.BuiltinMethodType, types.NoneType, types.NotImplementedType, types.EllipsisType,
        type(all.__call__)
        )

    def __init__(self, varName, varValue):
        super(ObjPythonMultilinePrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
        return [ (subitem, subitem) for subitem in dir(self.varValue) if hasattr(self.varValue, subitem) and not isinstance(getattr(self.varValue, subitem), self.excludeTypes) ]

    def getSubPrinter(self, fieldKey):
        return getMultilinePrinter(fieldKey, getattr(self.varValue,fieldKey))

class DictPythonMultilinePrinter(BasePythonMultilinePrinter):
    def __init__(self, varName, varValue):
        super(DictPythonMultilinePrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
        return map( lambda x, y: (x,y), self.varValue.keys(), self.varValue.keys() )

    def getSubPrinter(self, fieldKey):
        return getMultilinePrinter(fieldKey, self.varValue[fieldKey])


class ListPythonMultilinePrinter(BasePythonMultilinePrinter):
    def __init__(self, varName, varValue):
        super(ListPythonMultilinePrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
        return [ ("[%d]" % d, d) for d in xrange(min(0x100,len(self.varValue))) ]

    def getSubPrinter(self, subItemKey):
        arrayElem = self.varValue[subItemKey]
        return getMultilinePrinter("[%d]" % subItemKey, arrayElem)


class LongValuePrinter(BaseMultilinePrinter):

    def __init__(self, varName, varValue):
        super(LongValuePrinter,self).__init__(varName, varValue)

    def getVarShortValue(self):
        return long(self.varValue)

class StrValuePrinter(BaseMultilinePrinter):

    def __init__(self, varName, varValue):
        super(StrValuePrinter,self).__init__(varName, varValue)

    def getVarShortValue(self):
        return str(self.varValue)

class OffsetPrinter(BaseMultilinePrinter):

    def __init__(self, varName, varValue):
        super(OffsetPrinter,self).__init__(varName, varValue)

    def getVarShortValue(self):
        return pykd.findSymbol(self.varValue)

class MemoryInvalidPrinter(BaseMultilinePrinter):

    def __init__(self, varName, badaddress):
        super(MemoryInvalidPrinter,self).__init__(varName, None)

    def getVarShortValue(self):
        return "Invalid memory"

class TypedVarPrinter(BaseMultilinePrinter):

    def __init__(self, varName, varValue):
        super(TypedVarPrinter,self).__init__(varName, varValue)

    def getVarType(self):
        return self.varValue.type().name()

    def getVarShortValue(self):
        return getShortPrinter(self.varValue)

    def getVarLocation(self):
        locType, locVal = self.varValue.getLocation()
        if locType == pykd.Location.Reg:
            return '@' + locVal
        else:
            return hex(locVal)

class StructPrinter(TypedVarPrinter):

    def __init__(self, varName, varValue):
        super(StructPrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
        return map( lambda x,y: (x,y),  [ fieldName for fieldName, fieldType in self.varValue.type().fields() ], xrange(len(self.varValue.type().fields())) )

    def getSubPrinter(self, fieldNumber):
        return getMultilinePrinter(self.varValue.fieldName(fieldNumber), self.varValue.field(fieldNumber))

class PtrStructPrinter(TypedVarPrinter):

    def __init__(self, varName, varValue):
        super(PtrStructPrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
       fields = self.varValue.type().deref().fields()
       return map( lambda x,y: (x,y),  [ fieldName for fieldName, fieldType in fields ], xrange(len(fields)) )

    def getSubPrinter(self, fieldNumber):
        try:
            fieldName = self.varValue.type().deref().fieldName(fieldNumber)
            return getMultilinePrinter(fieldName, self.varValue.deref().field(fieldNumber))
        except pykd.MemoryException:
            return MemoryInvalidPrinter(fieldName, self.varValue.getAddress())


class PtrVtblPrinter(TypedVarPrinter):

    def __init__(self, varName, varValue):
        super(PtrVtblPrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
        addr = self.varValue.getAddress()
        if pykd.isValid(addr):
            return [ ( "[%d]" % i, i ) for i in xrange(len(self.varValue.deref())) ]
        else:
            return []

    def getSubPrinter(self, subItemKey):
        arrayElem = self.varValue.deref()[subItemKey]
        return OffsetPrinter("[%d]" % subItemKey, arrayElem)


class CustomArrayPrinter(TypedVarPrinter):

    def __init__(self, varName, varValue):
        super(CustomArrayPrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
        count = min(0x100, self.getElementCount())
        return [ ("[Raw]", "[Raw]") ] + [ ("[%d]" % i, i ) for i in xrange(count) ]

    def getSubPrinter(self, subItemKey):
        if subItemKey == "[Raw]":
            return StructPrinter(subItemKey, self.varValue)
        else:
            arrayElem = self.getElement(subItemKey)
            return getMultilinePrinter("[%d]" % subItemKey, arrayElem)

    @abstractmethod
    def getElement(self, i):
        pass

    @abstractmethod
    def getElementCount(self):
        pass

class ArrayPrinter(CustomArrayPrinter):

    def __init__(self, varName, varValue):
        super(ArrayPrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
        return [ ("[%d]" % d, d) for d in xrange(min(0x100,len(self.varValue))) ]

    def getSubPrinter(self, subItemKey):
       arrayElem = self.varValue[subItemKey]
       return getMultilinePrinter("[%d]" % subItemKey, arrayElem)


class TypeInfoPrinter(BaseMultilinePrinter):

    def __init__(self, varName, varValue):
        super(TypeInfoPrinter,self).__init__(varName, varValue)

    def getVarType(self):
        return self.varValue.name()

class StructTypePrinter(TypeInfoPrinter):

    def __init__(self, varName, varValue):
        super(StructTypePrinter,self).__init__(varName, varValue)

    def getVarSubitems(self):
       return map( lambda x,y: (x[0],y), self.varValue.fields(), xrange(len(self.varValue.fields())) )

    def getSubPrinter(self, fieldNumber):
        name = "+%04x  %s" % ( self.varValue.fieldOffset(fieldNumber), self.varValue.fieldName(fieldNumber))
        return getMultilinePrinter(name, self.varValue.field(fieldNumber))
    

shortPrinterList = []

def shortprinter(*typeNames):
    
    def decorator(fn):

        for typeName in typeNames:
            shortPrinterList.append( (typeName,fn,) )

        def wrapper(var):

            return fn(var)

        return wrapper

    return decorator

multilinePrinterList = []

def multilineprinter(*typeNames):

    def decorator(fn):

        for typeName in typeNames:
            multilinePrinterList.append( (typeName,fn,) )

        def wrapper(var):

            return fn(var)

        return wrapper

    return decorator

def registerVarPrinters():
    import karmadbg.varprinters
    registerVarPrintersInDir( karmadbg.varprinters.__path__[0] )

def registerVarPrintersInDir(path):
    for loader, module_name, ispkg in pkgutil.iter_modules([path]):
        if not ispkg:
            try:
                loader.find_module(module_name).load_module(module_name)
            except:
                print "Failed to register var printers from " + module_name
 
registerVarPrinters()





























