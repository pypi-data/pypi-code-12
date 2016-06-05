from __future__ import unicode_literals
try:
    import builtins
except:
    import __builtin__
    builtins = __builtin__
import functools

if hasattr(builtins,'unicode'):
    # python2 variant
    hxunicode = builtins.unicode
    hxunichr = builtins.unichr
    hxrange = xrange
    def hxnext(x):
        return x.next()
    if hasattr(functools,"cmp_to_key"):
        hx_cmp_to_key = functools.cmp_to_key
    else:
        # stretch to support python2.6
        def hx_cmp_to_key(mycmp):
            class K(object):
                def __init__(self, obj, *args):
                    self.obj = obj
                def __lt__(self, other):
                    return mycmp(self.obj, other.obj) < 0
                def __gt__(self, other):
                    return mycmp(self.obj, other.obj) > 0
                def __eq__(self, other):
                    return mycmp(self.obj, other.obj) == 0
                def __le__(self, other):
                    return mycmp(self.obj, other.obj) <= 0  
                def __ge__(self, other):
                    return mycmp(self.obj, other.obj) >= 0
                def __ne__(self, other):
                    return mycmp(self.obj, other.obj) != 0
            return K
else:
    # python3 variant
    hxunicode = str
    hxrange = range
    hxunichr = chr
    def hxnext(x):
        return x.__next__()
    hx_cmp_to_key = functools.cmp_to_key

python_lib_Builtin = builtins
String = builtins.str
python_lib_Dict = builtins.dict
python_lib_Set = builtins.set
import math as python_lib_Math
import math as Math
import os as python_lib_Os
import functools as python_lib_FuncTools
import inspect as python_lib_Inspect
import json as python_lib_Json
import codecs
import subprocess as python_lib_Subprocess
import sys as python_lib_Sys
from io import StringIO as python_lib_io_StringIO
from os import path as python_lib_os_Path




class _hx_ClassRegistry(python_lib_Dict):

	def __init__(self):
		super(_hx_ClassRegistry, self).__init__()

	def _register(self,cls,name):
		cls._hx_class = cls
		cls._hx_class_name = name
		self[name] = cls

	def registerAbstract(self,name):
		_g = self
		def _hx_local_0(cls):
			_g._register(cls,name)
			return cls
		wrapper = _hx_local_0
		return wrapper

	def registerEnum(self,name,constructs):
		_g = self
		def _hx_local_0(cls):
			_g._register(cls,name)
			cls._hx_constructs = constructs
			return cls
		wrapper = _hx_local_0
		return wrapper

	def registerClass(self,name,fields = None,props = None,methods = None,statics = None,interfaces = None,superClass = None):
		_g = self
		if (fields is None):
			fields = []
		if (props is None):
			props = []
		if (methods is None):
			methods = []
		if (statics is None):
			statics = []
		if (interfaces is None):
			interfaces = []
		def _hx_local_0(cls):
			_g._register(cls,name)
			cls._hx_fields = fields
			cls._hx_props = props
			cls._hx_methods = methods
			cls._hx_statics = statics
			cls._hx_interfaces = interfaces
			if (superClass is not None):
				cls._hx_super = superClass
			return cls
		wrapper = _hx_local_0
		return wrapper


class _hx_AnonObject(object):

	def __init__(self,fields):
		self.__dict__ = fields
_hx_classes = _hx_ClassRegistry()


class python_Boot(object):

	@staticmethod
	def arrayJoin(x,sep):
		return sep.join([python_Boot.toString1(x1,'') for x1 in x])

	@staticmethod
	def isPyBool(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.bool)

	@staticmethod
	def isPyInt(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.int)

	@staticmethod
	def isPyFloat(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.float)

	@staticmethod
	def isClass(o):
		return ((o is not None) and ((HxOverrides.eq(o,String) or python_lib_Inspect.isclass(o))))

	@staticmethod
	def isAnonObject(o):
		return python_lib_Builtin.isinstance(o,_hx_AnonObject)

	@staticmethod
	def _add_dynamic(a,b):
		if (python_lib_Builtin.isinstance(a,String) or python_lib_Builtin.isinstance(b,String)):
			return (python_Boot.toString1(a,"") + python_Boot.toString1(b,""))
		return (a + b)

	@staticmethod
	def toString(o):
		return python_Boot.toString1(o,"")

	@staticmethod
	def toString1(o,s):
		if (o is None):
			return "null"
		if python_lib_Builtin.isinstance(o,hxunicode):
			return o
		if (s is None):
			s = ""
		if (python_lib_Builtin.len(s) >= 5):
			return "<...>"
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.bool):
			if o:
				return "true"
			else:
				return "false"
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.int):
			return hxunicode(o)
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.float):
			try:
				if (o == python_lib_Builtin.int(o)):
					def _hx_local_1():
						def _hx_local_0():
							v = o
							return Math.floor((v + 0.5))
						return hxunicode(_hx_local_0())
					return _hx_local_1()
				else:
					return hxunicode(o)
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e = _hx_e1
				return hxunicode(o)
		if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
			o1 = o
			l = python_lib_Builtin.len(o1)
			st = "["
			s = (HxOverrides.stringOrNull(s) + "\t")
			_g = 0
			while ((_g < l)):
				i = _g
				_g = (_g + 1)
				prefix = ""
				if (i > 0):
					prefix = ","
				st = (HxOverrides.stringOrNull(st) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull(prefix) + HxOverrides.stringOrNull(python_Boot.toString1((o1[i] if i >= 0 and i < python_lib_Builtin.len(o1) else None),s))))))
			st = (HxOverrides.stringOrNull(st) + "]")
			return st
		try:
			if python_lib_Builtin.hasattr(o,"toString"):
				return o.toString()
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			pass
		if (python_lib_Inspect.isfunction(o) or python_lib_Inspect.ismethod(o)):
			return "<function>"
		if python_lib_Builtin.hasattr(o,"__class__"):
			if python_lib_Builtin.isinstance(o,_hx_AnonObject):
				toStr = None
				try:
					fields = python_Boot.fields(o)
					fieldsStr = None
					_g1 = []
					_g11 = 0
					while ((_g11 < python_lib_Builtin.len(fields))):
						f = (fields[_g11] if _g11 >= 0 and _g11 < python_lib_Builtin.len(fields) else None)
						_g11 = (_g11 + 1)
						x = ((("" + HxOverrides.stringOrNull(f)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.field(o,f),(HxOverrides.stringOrNull(s) + "\t"))))
						_g1.append(x)
						python_lib_Builtin.len(_g1)
					fieldsStr = _g1
					toStr = (("{ " + HxOverrides.stringOrNull(", ".join([python_Boot.toString1(x1,'') for x1 in fieldsStr]))) + " }")
				except Exception as _hx_e:
					_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
					e2 = _hx_e1
					return "{ ... }"
				if (toStr is None):
					return "{ ... }"
				else:
					return toStr
			if python_lib_Builtin.isinstance(o,Enum):
				o2 = o
				l1 = python_lib_Builtin.len(o2.params)
				hasParams = (l1 > 0)
				if hasParams:
					paramsStr = ""
					_g2 = 0
					while ((_g2 < l1)):
						i1 = _g2
						_g2 = (_g2 + 1)
						prefix1 = ""
						if (i1 > 0):
							prefix1 = ","
						paramsStr = (HxOverrides.stringOrNull(paramsStr) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull(prefix1) + HxOverrides.stringOrNull(python_Boot.toString1((o2.params[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(o2.params) else None),s))))))
					return (((HxOverrides.stringOrNull(o2.tag) + "(") + HxOverrides.stringOrNull(paramsStr)) + ")")
				else:
					return o2.tag
			if python_lib_Builtin.hasattr(o,"_hx_class_name"):
				if (o.__class__.__name__ != "type"):
					fields1 = python_Boot.getInstanceFields(o)
					fieldsStr1 = None
					_g3 = []
					_g12 = 0
					while ((_g12 < python_lib_Builtin.len(fields1))):
						f1 = (fields1[_g12] if _g12 >= 0 and _g12 < python_lib_Builtin.len(fields1) else None)
						_g12 = (_g12 + 1)
						x1 = ((("" + HxOverrides.stringOrNull(f1)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.field(o,f1),(HxOverrides.stringOrNull(s) + "\t"))))
						_g3.append(x1)
						python_lib_Builtin.len(_g3)
					fieldsStr1 = _g3
					toStr1 = (((Std.string(o._hx_class_name) + "( ") + HxOverrides.stringOrNull(", ".join([python_Boot.toString1(x1,'') for x1 in fieldsStr1]))) + " )")
					return toStr1
				else:
					fields2 = python_Boot.getClassFields(o)
					fieldsStr2 = None
					_g4 = []
					_g13 = 0
					while ((_g13 < python_lib_Builtin.len(fields2))):
						f2 = (fields2[_g13] if _g13 >= 0 and _g13 < python_lib_Builtin.len(fields2) else None)
						_g13 = (_g13 + 1)
						x2 = ((("" + HxOverrides.stringOrNull(f2)) + " : ") + HxOverrides.stringOrNull(python_Boot.toString1(python_Boot.field(o,f2),(HxOverrides.stringOrNull(s) + "\t"))))
						_g4.append(x2)
						python_lib_Builtin.len(_g4)
					fieldsStr2 = _g4
					toStr2 = (((("#" + Std.string(o._hx_class_name)) + "( ") + HxOverrides.stringOrNull(", ".join([python_Boot.toString1(x1,'') for x1 in fieldsStr2]))) + " )")
					return toStr2
			if (o == String):
				return "#String"
			if (o == list):
				return "#Array"
			if python_lib_Builtin.callable(o):
				return "function"
			try:
				if python_lib_Builtin.hasattr(o,"__repr__"):
					return o.__repr__()
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				pass
			if python_lib_Builtin.hasattr(o,"__str__"):
				return o.__str__([])
			if python_lib_Builtin.hasattr(o,"__name__"):
				return o.__name__
			return "???"
		else:
			return hxunicode(o)

	@staticmethod
	def isMetaType(v,t):
		return (v == t)

	@staticmethod
	def fields(o):
		a = []
		if (o is not None):
			if python_lib_Builtin.hasattr(o,"_hx_fields"):
				fields = o._hx_fields
				return python_lib_Builtin.list(fields)
			if python_lib_Builtin.isinstance(o,_hx_AnonObject):
				d = o.__dict__
				keys = d.keys()
				handler = python_Boot.unhandleKeywords
				for k in keys:
					a.append(handler(k))
			elif python_lib_Builtin.hasattr(o,"__dict__"):
				a1 = []
				d1 = o.__dict__
				keys1 = d1.keys()
				for k in keys1:
					a.append(k)
		return a

	@staticmethod
	def isString(o):
		return python_lib_Builtin.isinstance(o,hxunicode)

	@staticmethod
	def isArray(o):
		return python_lib_Builtin.isinstance(o,python_lib_Builtin.list)

	@staticmethod
	def field(o,field):
		if (field is None):
			return None
		_hx_local_0 = python_lib_Builtin.len((field))
		if (_hx_local_0 == 10):
			if ((field) == "charCodeAt"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s4 = o
					def _hx_local_1(a11):
						return HxString.charCodeAt(s4,a11)
					return _hx_local_1
		elif (_hx_local_0 == 11):
			if ((field) == "toLowerCase"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s1 = o
					def _hx_local_2():
						return HxString.toLowerCase(s1)
					return _hx_local_2
			elif ((field) == "toUpperCase"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s2 = o
					def _hx_local_3():
						return HxString.toUpperCase(s2)
					return _hx_local_3
			elif ((field) == "lastIndexOf"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s6 = o
					def _hx_local_4(a13):
						return HxString.lastIndexOf(s6,a13)
					return _hx_local_4
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a2 = o
					def _hx_local_5(x2):
						return python_internal_ArrayImpl.lastIndexOf(a2,x2)
					return _hx_local_5
		elif (_hx_local_0 == 9):
			if ((field) == "substring"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s9 = o
					def _hx_local_6(a15):
						return HxString.substring(s9,a15)
					return _hx_local_6
		elif (_hx_local_0 == 5):
			if ((field) == "split"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s7 = o
					def _hx_local_7(d):
						return HxString.split(s7,d)
					return _hx_local_7
			elif ((field) == "shift"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x14 = o
					def _hx_local_8():
						return python_internal_ArrayImpl.shift(x14)
					return _hx_local_8
			elif ((field) == "slice"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x15 = o
					def _hx_local_9(a18):
						return python_internal_ArrayImpl.slice(x15,a18)
					return _hx_local_9
		elif (_hx_local_0 == 4):
			if ((field) == "copy"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					def _hx_local_10():
						x6 = o
						return python_lib_Builtin.list(x6)
					return _hx_local_10
			elif ((field) == "join"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					def _hx_local_11(sep):
						x9 = o
						return sep.join([python_Boot.toString1(x1,'') for x1 in x9])
					return _hx_local_11
			elif ((field) == "push"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x11 = o
					def _hx_local_12(e):
						return python_internal_ArrayImpl.push(x11,e)
					return _hx_local_12
			elif ((field) == "sort"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x16 = o
					def _hx_local_13(f2):
						python_internal_ArrayImpl.sort(x16,f2)
					return _hx_local_13
		elif (_hx_local_0 == 7):
			if ((field) == "indexOf"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s5 = o
					def _hx_local_14(a12):
						return HxString.indexOf(s5,a12)
					return _hx_local_14
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a = o
					def _hx_local_15(x1):
						return python_internal_ArrayImpl.indexOf(a,x1)
					return _hx_local_15
			elif ((field) == "unshift"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x12 = o
					def _hx_local_16(e1):
						python_internal_ArrayImpl.unshift(x12,e1)
					return _hx_local_16
			elif ((field) == "reverse"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a4 = o
					def _hx_local_17():
						python_internal_ArrayImpl.reverse(a4)
					return _hx_local_17
		elif (_hx_local_0 == 3):
			if ((field) == "map"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x4 = o
					def _hx_local_18(f):
						return python_internal_ArrayImpl.map(x4,f)
					return _hx_local_18
			elif ((field) == "pop"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x10 = o
					def _hx_local_19():
						return python_internal_ArrayImpl.pop(x10)
					return _hx_local_19
		elif (_hx_local_0 == 8):
			if ((field) == "toString"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s10 = o
					def _hx_local_20():
						return HxString.toString(s10)
					return _hx_local_20
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x3 = o
					def _hx_local_21():
						return python_internal_ArrayImpl.toString(x3)
					return _hx_local_21
			elif ((field) == "iterator"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x7 = o
					def _hx_local_22():
						return python_internal_ArrayImpl.iterator(x7)
					return _hx_local_22
		elif (_hx_local_0 == 6):
			if ((field) == "length"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s = o
					return python_lib_Builtin.len(s)
				elif python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x = o
					return python_lib_Builtin.len(x)
			elif ((field) == "charAt"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s3 = o
					def _hx_local_23(a1):
						return HxString.charAt(s3,a1)
					return _hx_local_23
			elif ((field) == "substr"):
				if python_lib_Builtin.isinstance(o,hxunicode):
					s8 = o
					def _hx_local_24(a14):
						return HxString.substr(s8,a14)
					return _hx_local_24
			elif ((field) == "filter"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x5 = o
					def _hx_local_25(f1):
						return python_internal_ArrayImpl.filter(x5,f1)
					return _hx_local_25
			elif ((field) == "concat"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a16 = o
					def _hx_local_26(a21):
						return python_internal_ArrayImpl.concat(a16,a21)
					return _hx_local_26
			elif ((field) == "insert"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					a3 = o
					def _hx_local_27(a17,x8):
						python_internal_ArrayImpl.insert(a3,a17,x8)
					return _hx_local_27
			elif ((field) == "remove"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x13 = o
					def _hx_local_28(e2):
						return python_internal_ArrayImpl.remove(x13,e2)
					return _hx_local_28
			elif ((field) == "splice"):
				if python_lib_Builtin.isinstance(o,python_lib_Builtin.list):
					x17 = o
					def _hx_local_29(a19,a22):
						return python_internal_ArrayImpl.splice(x17,a19,a22)
					return _hx_local_29
		else:
			pass
		field1 = None
		if field in python_Boot.keywords:
			field1 = ("_hx_" + field)
		elif ((((python_lib_Builtin.len(field) > 2) and ((python_lib_Builtin.ord(field[0]) == 95))) and ((python_lib_Builtin.ord(field[1]) == 95))) and ((python_lib_Builtin.ord(field[(python_lib_Builtin.len(field) - 1)]) != 95))):
			field1 = ("_hx_" + field)
		else:
			field1 = field
		if python_lib_Builtin.hasattr(o,field1):
			return python_lib_Builtin.getattr(o,field1)
		else:
			return None

	@staticmethod
	def getInstanceFields(c):
		f = None
		if python_lib_Builtin.hasattr(c,"_hx_fields"):
			x = c._hx_fields
			x2 = c._hx_methods
			f = (x + x2)
		else:
			f = []
		sc = python_Boot.getSuperClass(c)
		if (sc is None):
			return f
		else:
			scArr = python_Boot.getInstanceFields(sc)
			scMap = None
			_g = haxe_ds_StringMap()
			_g1 = 0
			while ((_g1 < python_lib_Builtin.len(scArr))):
				f1 = (scArr[_g1] if _g1 >= 0 and _g1 < python_lib_Builtin.len(scArr) else None)
				_g1 = (_g1 + 1)
				_g.h[f1] = f1
			scMap = _g
			res = []
			_g11 = 0
			while ((_g11 < python_lib_Builtin.len(f))):
				f11 = (f[_g11] if _g11 >= 0 and _g11 < python_lib_Builtin.len(f) else None)
				_g11 = (_g11 + 1)
				if (not f11 in scMap.h):
					scArr.append(f11)
					python_lib_Builtin.len(scArr)
			return scArr

	@staticmethod
	def getSuperClass(c):
		if (c is None):
			return None
		try:
			if python_lib_Builtin.hasattr(c,"_hx_super"):
				return c._hx_super
			return None
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			pass
		return None

	@staticmethod
	def getClassFields(c):
		if python_lib_Builtin.hasattr(c,"_hx_statics"):
			x = c._hx_statics
			return python_lib_Builtin.list(x)
		else:
			return []

	@staticmethod
	def unsafeFastCodeAt(s,index):
		return python_lib_Builtin.ord(s[index])

	@staticmethod
	def handleKeywords(name):
		if name in python_Boot.keywords:
			return ("_hx_" + name)
		elif ((((python_lib_Builtin.len(name) > 2) and ((python_lib_Builtin.ord(name[0]) == 95))) and ((python_lib_Builtin.ord(name[1]) == 95))) and ((python_lib_Builtin.ord(name[(python_lib_Builtin.len(name) - 1)]) != 95))):
			return ("_hx_" + name)
		else:
			return name

	@staticmethod
	def unhandleKeywords(name):
		if (HxString.substr(name,0,python_Boot.prefixLength) == "_hx_"):
			real = HxString.substr(name,python_Boot.prefixLength,None)
			if real in python_Boot.keywords:
				return real
		return name


python_Boot = _hx_classes.registerClass("python.Boot", statics=["keywords","arrayJoin","isPyBool","isPyInt","isPyFloat","isClass","isAnonObject","_add_dynamic","toString","toString1","isMetaType","fields","isString","isArray","field","getInstanceFields","getSuperClass","getClassFields","unsafeFastCodeAt","handleKeywords","prefixLength","unhandleKeywords"])(python_Boot)

class Enum(object):

	def __init__(self,tag,index,params):
		self.tag = None
		self.index = None
		self.params = None
		self.tag = tag
		self.index = index
		self.params = params

	def __str__(self):
		if (self.params is None):
			return self.tag
		else:
			return (((HxOverrides.stringOrNull(self.tag) + "(") + HxOverrides.stringOrNull(",".join([python_Boot.toString1(x1,'') for x1 in self.params]))) + ")")

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.tag = None
		_hx_o.index = None
		_hx_o.params = None


Enum = _hx_classes.registerClass("Enum", fields=["tag","index","params"], methods=["__str__"])(Enum)

class HxOverrides(object):

	@staticmethod
	def iterator(x):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return python_HaxeIterator(x.__iter__())
		return x.iterator()

	@staticmethod
	def eq(a,b):
		if (python_lib_Builtin.isinstance(a,python_lib_Builtin.list) or python_lib_Builtin.isinstance(b,python_lib_Builtin.list)):
			return a is b
		return (a == b)

	@staticmethod
	def stringOrNull(s):
		if (s is None):
			return "null"
		else:
			return s

	@staticmethod
	def shift(x):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			_this = x
			return (None if ((python_lib_Builtin.len(_this) == 0)) else _this.pop(0))
		return x.shift()

	@staticmethod
	def pop(x):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			_this = x
			return (None if ((python_lib_Builtin.len(_this) == 0)) else _this.pop())
		return x.pop()

	@staticmethod
	def push(x,e):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			_this = x
			_this.append(e)
			return python_lib_Builtin.len(_this)
		return x.push(e)

	@staticmethod
	def join(x,sep):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return sep.join([python_Boot.toString1(x1,'') for x1 in x])
		return x.join(sep)

	@staticmethod
	def filter(x,f):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return python_lib_Builtin.list(python_lib_Builtin.filter(f,x))
		return x.filter(f)

	@staticmethod
	def map(x,f):
		if python_lib_Builtin.isinstance(x,python_lib_Builtin.list):
			return python_lib_Builtin.list(python_lib_Builtin.map(f,x))
		return x.map(f)

	@staticmethod
	def toUpperCase(x):
		if python_lib_Builtin.isinstance(x,hxunicode):
			return x.upper()
		return x.toUpperCase()

	@staticmethod
	def toLowerCase(x):
		if python_lib_Builtin.isinstance(x,hxunicode):
			return x.lower()
		return x.toLowerCase()

	@staticmethod
	def rshift(val,n):
		return ((val % 0x100000000) >> n)

	@staticmethod
	def modf(a,b):
		return float('nan') if (b == 0.0) else a % b if a > 0 else -(-a % b)

	@staticmethod
	def arrayGet(a,i):
		if python_lib_Builtin.isinstance(a,python_lib_Builtin.list):
			x = a
			if ((i > -1) and ((i < python_lib_Builtin.len(x)))):
				return x[i]
			else:
				return None
		else:
			return a[i]

	@staticmethod
	def arraySet(a,i,v):
		if python_lib_Builtin.isinstance(a,python_lib_Builtin.list):
			x = a
			v1 = v
			l = python_lib_Builtin.len(x)
			while ((l < i)):
				x.append(None)
				python_lib_Builtin.len(x)
				l = (l + 1)
			if (l == i):
				x.append(v1)
				python_lib_Builtin.len(x)
			else:
				x[i] = v1
			return v1
		else:
			a[i] = v
			return v


HxOverrides = _hx_classes.registerClass("HxOverrides", statics=["iterator","eq","stringOrNull","shift","pop","push","join","filter","map","toUpperCase","toLowerCase","rshift","modf","arrayGet","arraySet"])(HxOverrides)

class Alignment(object):

	def __init__(self):
		self.map_a2b = None
		self.map_b2a = None
		self.ha = None
		self.hb = None
		self.ta = None
		self.tb = None
		self.ia = None
		self.ib = None
		self.map_count = None
		self.order_cache = None
		self.order_cache_has_reference = None
		self.index_columns = None
		self.marked_as_identical = None
		self.reference = None
		self.meta = None
		self.comp = None
		self.has_addition = None
		self.has_removal = None
		self.map_a2b = haxe_ds_IntMap()
		self.map_b2a = haxe_ds_IntMap()
		def _hx_local_0():
			self.hb = 0
			return self.hb
		self.ha = _hx_local_0()
		self.map_count = 0
		self.reference = None
		self.meta = None
		self.comp = None
		self.order_cache_has_reference = False
		self.ia = -1
		self.ib = -1
		self.marked_as_identical = False

	def range(self,ha,hb):
		self.ha = ha
		self.hb = hb

	def tables(self,ta,tb):
		self.ta = ta
		self.tb = tb

	def headers(self,ia,ib):
		self.ia = ia
		self.ib = ib

	def setRowlike(self,flag):
		pass

	def link(self,a,b):
		if (a != -1):
			self.map_a2b.set(a,b)
		else:
			self.has_addition = True
		if (b != -1):
			self.map_b2a.set(b,a)
		else:
			self.has_removal = True
		_hx_local_0 = self
		_hx_local_1 = _hx_local_0.map_count
		_hx_local_0.map_count = (_hx_local_1 + 1)
		_hx_local_1

	def addIndexColumns(self,unit):
		if (self.index_columns is None):
			self.index_columns = list()
		_this = self.index_columns
		_this.append(unit)
		python_lib_Builtin.len(_this)

	def getIndexColumns(self):
		return self.index_columns

	def a2b(self,a):
		return self.map_a2b.h.get(a,None)

	def b2a(self,b):
		return self.map_b2a.h.get(b,None)

	def count(self):
		return self.map_count

	def toString(self):
		result = ((("" + HxOverrides.stringOrNull(self.map_a2b.toString())) + " // ") + HxOverrides.stringOrNull(self.map_b2a.toString()))
		if (self.reference is not None):
			result = (HxOverrides.stringOrNull(result) + (((" (" + Std.string(self.reference)) + ")")))
		return result

	def toOrder(self):
		if (self.order_cache is not None):
			if (self.reference is not None):
				if (not self.order_cache_has_reference):
					self.order_cache = None
		if (self.order_cache is None):
			self.order_cache = self.toOrder3()
		if (self.reference is not None):
			self.order_cache_has_reference = True
		return self.order_cache

	def addToOrder(self,l,r,p = -2):
		if (p is None):
			p = -2
		if (self.order_cache is None):
			self.order_cache = Ordering()
		self.order_cache.add(l,r,p)
		self.order_cache_has_reference = (p != -2)

	def getSource(self):
		return self.ta

	def getTarget(self):
		return self.tb

	def getSourceHeader(self):
		return self.ia

	def getTargetHeader(self):
		return self.ib

	def toOrder3(self):
		order = list()
		if (self.reference is None):
			_hx_local_0 = self.map_a2b.keys()
			while (_hx_local_0.hasNext()):
				k = hxnext(_hx_local_0)
				unit = Unit()
				unit.l = k
				unit.r = self.a2b(k)
				order.append(unit)
				python_lib_Builtin.len(order)
			_hx_local_1 = self.map_b2a.keys()
			while (_hx_local_1.hasNext()):
				k1 = hxnext(_hx_local_1)
				if (self.b2a(k1) == -1):
					unit1 = Unit()
					unit1.l = -1
					unit1.r = k1
					order.append(unit1)
					python_lib_Builtin.len(order)
		else:
			_hx_local_2 = self.map_a2b.keys()
			while (_hx_local_2.hasNext()):
				k2 = hxnext(_hx_local_2)
				unit2 = Unit()
				unit2.p = k2
				unit2.l = self.reference.a2b(k2)
				unit2.r = self.a2b(k2)
				order.append(unit2)
				python_lib_Builtin.len(order)
			_hx_local_3 = self.reference.map_b2a.keys()
			while (_hx_local_3.hasNext()):
				k3 = hxnext(_hx_local_3)
				if (self.reference.b2a(k3) == -1):
					unit3 = Unit()
					unit3.p = -1
					unit3.l = k3
					unit3.r = -1
					order.append(unit3)
					python_lib_Builtin.len(order)
			_hx_local_4 = self.map_b2a.keys()
			while (_hx_local_4.hasNext()):
				k4 = hxnext(_hx_local_4)
				if (self.b2a(k4) == -1):
					unit4 = Unit()
					unit4.p = -1
					unit4.l = -1
					unit4.r = k4
					order.append(unit4)
					python_lib_Builtin.len(order)
		top = python_lib_Builtin.len(order)
		remotes = list()
		locals = list()
		_g = 0
		while ((_g < top)):
			o = _g
			_g = (_g + 1)
			if ((order[o] if o >= 0 and o < python_lib_Builtin.len(order) else None).r >= 0):
				remotes.append(o)
				python_lib_Builtin.len(remotes)
			else:
				locals.append(o)
				python_lib_Builtin.len(locals)
		def _hx_local_5(a,b):
			return ((order[a] if a >= 0 and a < python_lib_Builtin.len(order) else None).r - (order[b] if b >= 0 and b < python_lib_Builtin.len(order) else None).r)
		remote_sort = _hx_local_5
		def _hx_local_6(a1,b1):
			if (a1 == b1):
				return 0
			if (((order[a1] if a1 >= 0 and a1 < python_lib_Builtin.len(order) else None).l >= 0) and (((order[b1] if b1 >= 0 and b1 < python_lib_Builtin.len(order) else None).l >= 0))):
				return ((order[a1] if a1 >= 0 and a1 < python_lib_Builtin.len(order) else None).l - (order[b1] if b1 >= 0 and b1 < python_lib_Builtin.len(order) else None).l)
			if ((order[a1] if a1 >= 0 and a1 < python_lib_Builtin.len(order) else None).l >= 0):
				return 1
			if ((order[b1] if b1 >= 0 and b1 < python_lib_Builtin.len(order) else None).l >= 0):
				return -1
			return (a1 - b1)
		local_sort = _hx_local_6
		if (self.reference is not None):
			def _hx_local_7(a2,b2):
				if (a2 == b2):
					return 0
				o1 = ((order[a2] if a2 >= 0 and a2 < python_lib_Builtin.len(order) else None).r - (order[b2] if b2 >= 0 and b2 < python_lib_Builtin.len(order) else None).r)
				if (((order[a2] if a2 >= 0 and a2 < python_lib_Builtin.len(order) else None).p >= 0) and (((order[b2] if b2 >= 0 and b2 < python_lib_Builtin.len(order) else None).p >= 0))):
					o2 = ((order[a2] if a2 >= 0 and a2 < python_lib_Builtin.len(order) else None).p - (order[b2] if b2 >= 0 and b2 < python_lib_Builtin.len(order) else None).p)
					if ((o1 * o2) < 0):
						return o1
					o3 = ((order[a2] if a2 >= 0 and a2 < python_lib_Builtin.len(order) else None).l - (order[b2] if b2 >= 0 and b2 < python_lib_Builtin.len(order) else None).l)
					return o3
				return o1
			remote_sort = _hx_local_7
			def _hx_local_8(a3,b3):
				if (a3 == b3):
					return 0
				if (((order[a3] if a3 >= 0 and a3 < python_lib_Builtin.len(order) else None).l >= 0) and (((order[b3] if b3 >= 0 and b3 < python_lib_Builtin.len(order) else None).l >= 0))):
					o11 = ((order[a3] if a3 >= 0 and a3 < python_lib_Builtin.len(order) else None).l - (order[b3] if b3 >= 0 and b3 < python_lib_Builtin.len(order) else None).l)
					if (((order[a3] if a3 >= 0 and a3 < python_lib_Builtin.len(order) else None).p >= 0) and (((order[b3] if b3 >= 0 and b3 < python_lib_Builtin.len(order) else None).p >= 0))):
						o21 = ((order[a3] if a3 >= 0 and a3 < python_lib_Builtin.len(order) else None).p - (order[b3] if b3 >= 0 and b3 < python_lib_Builtin.len(order) else None).p)
						if ((o11 * o21) < 0):
							return o11
						return o21
				if ((order[a3] if a3 >= 0 and a3 < python_lib_Builtin.len(order) else None).l >= 0):
					return 1
				if ((order[b3] if b3 >= 0 and b3 < python_lib_Builtin.len(order) else None).l >= 0):
					return -1
				return (a3 - b3)
			local_sort = _hx_local_8
		remotes.sort(key= hx_cmp_to_key(remote_sort))
		locals.sort(key= hx_cmp_to_key(local_sort))
		revised_order = list()
		at_r = 0
		at_l = 0
		_g1 = 0
		while ((_g1 < top)):
			o4 = _g1
			_g1 = (_g1 + 1)
			if ((at_r < python_lib_Builtin.len(remotes)) and ((at_l < python_lib_Builtin.len(locals)))):
				ur = python_internal_ArrayImpl._get(order, (remotes[at_r] if at_r >= 0 and at_r < python_lib_Builtin.len(remotes) else None))
				ul = python_internal_ArrayImpl._get(order, (locals[at_l] if at_l >= 0 and at_l < python_lib_Builtin.len(locals) else None))
				if (((ul.l == -1) and ((ul.p >= 0))) and ((ur.p >= 0))):
					if (ur.p > ul.p):
						revised_order.append(ul)
						python_lib_Builtin.len(revised_order)
						at_l = (at_l + 1)
						continue
				elif (ur.l > ul.l):
					revised_order.append(ul)
					python_lib_Builtin.len(revised_order)
					at_l = (at_l + 1)
					continue
				revised_order.append(ur)
				python_lib_Builtin.len(revised_order)
				at_r = (at_r + 1)
				continue
			if (at_r < python_lib_Builtin.len(remotes)):
				ur1 = python_internal_ArrayImpl._get(order, (remotes[at_r] if at_r >= 0 and at_r < python_lib_Builtin.len(remotes) else None))
				revised_order.append(ur1)
				python_lib_Builtin.len(revised_order)
				at_r = (at_r + 1)
				continue
			if (at_l < python_lib_Builtin.len(locals)):
				ul1 = python_internal_ArrayImpl._get(order, (locals[at_l] if at_l >= 0 and at_l < python_lib_Builtin.len(locals) else None))
				revised_order.append(ul1)
				python_lib_Builtin.len(revised_order)
				at_l = (at_l + 1)
				continue
		order = revised_order
		result = Ordering()
		result.setList(order)
		if (self.reference is None):
			result.ignoreParent()
		return result

	def markIdentical(self):
		self.marked_as_identical = True

	def isMarkedAsIdentical(self):
		return self.marked_as_identical

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.map_a2b = None
		_hx_o.map_b2a = None
		_hx_o.ha = None
		_hx_o.hb = None
		_hx_o.ta = None
		_hx_o.tb = None
		_hx_o.ia = None
		_hx_o.ib = None
		_hx_o.map_count = None
		_hx_o.order_cache = None
		_hx_o.order_cache_has_reference = None
		_hx_o.index_columns = None
		_hx_o.marked_as_identical = None
		_hx_o.reference = None
		_hx_o.meta = None
		_hx_o.comp = None
		_hx_o.has_addition = None
		_hx_o.has_removal = None


Alignment = _hx_classes.registerClass("Alignment", fields=["map_a2b","map_b2a","ha","hb","ta","tb","ia","ib","map_count","order_cache","order_cache_has_reference","index_columns","marked_as_identical","reference","meta","comp","has_addition","has_removal"], methods=["range","tables","headers","setRowlike","link","addIndexColumns","getIndexColumns","a2b","b2a","count","toString","toOrder","addToOrder","getSource","getTarget","getSourceHeader","getTargetHeader","toOrder3","markIdentical","isMarkedAsIdentical"])(Alignment)

class python_internal_ArrayImpl(object):

	@staticmethod
	def get_length(x):
		return python_lib_Builtin.len(x)

	@staticmethod
	def concat(a1,a2):
		return (a1 + a2)

	@staticmethod
	def copy(x):
		return python_lib_Builtin.list(x)

	@staticmethod
	def iterator(x):
		return python_HaxeIterator(x.__iter__())

	@staticmethod
	def indexOf(a,x,fromIndex = None):
		len = python_lib_Builtin.len(a)
		l = None
		if (fromIndex is None):
			l = 0
		elif (fromIndex < 0):
			l = (len + fromIndex)
		else:
			l = fromIndex
		if (l < 0):
			l = 0
		_g = l
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			if (a[i] == x):
				return i
		return -1

	@staticmethod
	def lastIndexOf(a,x,fromIndex = None):
		len = python_lib_Builtin.len(a)
		l = None
		if (fromIndex is None):
			l = len
		elif (fromIndex < 0):
			l = ((len + fromIndex) + 1)
		else:
			l = (fromIndex + 1)
		if (l > len):
			l = len
		l = (l - 1)
		while ((l > -1)):
			if (a[l] == x):
				return l
			l = (l - 1)
		return -1

	@staticmethod
	def join(x,sep):
		return sep.join([python_Boot.toString1(x1,'') for x1 in x])

	@staticmethod
	def toString(x):
		return (("[" + HxOverrides.stringOrNull(",".join([python_Boot.toString1(x1,'') for x1 in x]))) + "]")

	@staticmethod
	def pop(x):
		if (python_lib_Builtin.len(x) == 0):
			return None
		else:
			return x.pop()

	@staticmethod
	def push(x,e):
		x.append(e)
		return python_lib_Builtin.len(x)

	@staticmethod
	def unshift(x,e):
		x.insert(0, e)

	@staticmethod
	def remove(x,e):
		try:
			x.remove(e)
			return True
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e1 = _hx_e1
			return False

	@staticmethod
	def shift(x):
		if (python_lib_Builtin.len(x) == 0):
			return None
		return x.pop(0)

	@staticmethod
	def slice(x,pos,end = None):
		return x[pos:end]

	@staticmethod
	def sort(x,f):
		x.sort(key= hx_cmp_to_key(f))

	@staticmethod
	def splice(x,pos,len):
		if (pos < 0):
			pos = (python_lib_Builtin.len(x) + pos)
		if (pos < 0):
			pos = 0
		res = x[pos:(pos + len)]
		del x[pos:(pos + len)]
		return res

	@staticmethod
	def map(x,f):
		return python_lib_Builtin.list(python_lib_Builtin.map(f,x))

	@staticmethod
	def filter(x,f):
		return python_lib_Builtin.list(python_lib_Builtin.filter(f,x))

	@staticmethod
	def insert(a,pos,x):
		a.insert(pos, x)

	@staticmethod
	def reverse(a):
		a.reverse()

	@staticmethod
	def _get(x,idx):
		if ((idx > -1) and ((idx < python_lib_Builtin.len(x)))):
			return x[idx]
		else:
			return None

	@staticmethod
	def _set(x,idx,v):
		l = python_lib_Builtin.len(x)
		while ((l < idx)):
			x.append(None)
			python_lib_Builtin.len(x)
			l = (l + 1)
		if (l == idx):
			x.append(v)
			python_lib_Builtin.len(x)
		else:
			x[idx] = v
		return v

	@staticmethod
	def unsafeGet(x,idx):
		return x[idx]

	@staticmethod
	def unsafeSet(x,idx,val):
		x[idx] = val
		return val


python_internal_ArrayImpl = _hx_classes.registerClass("python.internal.ArrayImpl", statics=["get_length","concat","copy","iterator","indexOf","lastIndexOf","join","toString","pop","push","unshift","remove","shift","slice","sort","splice","map","filter","insert","reverse","_get","_set","unsafeGet","unsafeSet"])(python_internal_ArrayImpl)

class CellBuilder(object):
	pass
CellBuilder = _hx_classes.registerClass("CellBuilder", methods=["needSeparator","setSeparator","setConflictSeparator","setView","update","conflict","marker","links"])(CellBuilder)

class CellInfo(object):

	def __init__(self):
		self.raw = None
		self.value = None
		self.pretty_value = None
		self.category = None
		self.category_given_tr = None
		self.separator = None
		self.pretty_separator = None
		self.updated = None
		self.conflicted = None
		self.pvalue = None
		self.lvalue = None
		self.rvalue = None
		self.meta = None
		pass

	def toString(self):
		if (not self.updated):
			return self.value
		if (not self.conflicted):
			return ((HxOverrides.stringOrNull(self.lvalue) + "::") + HxOverrides.stringOrNull(self.rvalue))
		return ((((HxOverrides.stringOrNull(self.pvalue) + "||") + HxOverrides.stringOrNull(self.lvalue)) + "::") + HxOverrides.stringOrNull(self.rvalue))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.raw = None
		_hx_o.value = None
		_hx_o.pretty_value = None
		_hx_o.category = None
		_hx_o.category_given_tr = None
		_hx_o.separator = None
		_hx_o.pretty_separator = None
		_hx_o.updated = None
		_hx_o.conflicted = None
		_hx_o.pvalue = None
		_hx_o.lvalue = None
		_hx_o.rvalue = None
		_hx_o.meta = None


CellInfo = _hx_classes.registerClass("CellInfo", fields=["raw","value","pretty_value","category","category_given_tr","separator","pretty_separator","updated","conflicted","pvalue","lvalue","rvalue","meta"], methods=["toString"])(CellInfo)

class Class(object):
	pass
Class = _hx_classes.registerAbstract("Class")(Class)

class ColumnChange(object):

	def __init__(self):
		self.prevName = None
		self.name = None
		self.props = None
		pass

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.prevName = None
		_hx_o.name = None
		_hx_o.props = None


ColumnChange = _hx_classes.registerClass("ColumnChange", fields=["prevName","name","props"])(ColumnChange)

class Table(object):
	pass
Table = _hx_classes.registerClass("Table", methods=["getCell","setCell","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","get_width","get_height","getData","clone","create","getMeta"])(Table)

class CombinedTable(object):

	def __init__(self,t):
		self.t = None
		self.body = None
		self.head = None
		self.dx = None
		self.dy = None
		self.core = None
		self.meta = None
		self.t = t
		self.dx = 0
		self.dy = 0
		self.core = t
		self.head = None
		if ((t.get_width() < 1) or ((t.get_height() < 1))):
			return
		v = t.getCellView()
		if (v.toString(t.getCell(0,0)) != "@@"):
			return
		self.dx = 1
		self.dy = 0
		_g1 = 0
		_g = t.get_height()
		while ((_g1 < _g)):
			y = _g1
			_g1 = (_g1 + 1)
			txt = v.toString(t.getCell(0,y))
			if (((txt is None) or ((txt == ""))) or ((txt == "null"))):
				break
			_hx_local_0 = self
			_hx_local_1 = _hx_local_0.dy
			_hx_local_0.dy = (_hx_local_1 + 1)
			_hx_local_1
		self.head = CombinedTableHead(self, self.dx, self.dy)
		self.body = CombinedTableBody(self, self.dx, self.dy)
		self.core = self.body
		self.meta = SimpleMeta(self.head)

	def all(self):
		return self.t

	def getTable(self):
		return self

	def get_width(self):
		return self.core.get_width()

	def get_height(self):
		return self.core.get_height()

	def getCell(self,x,y):
		return self.core.getCell(x,y)

	def setCell(self,x,y,c):
		self.core.setCell(x,y,c)

	def toString(self):
		return SimpleTable.tableToString(self)

	def getCellView(self):
		return self.t.getCellView()

	def isResizable(self):
		return self.core.isResizable()

	def resize(self,w,h):
		return self.core.resize(h,w)

	def clear(self):
		self.core.clear()

	def insertOrDeleteRows(self,fate,hfate):
		return self.core.insertOrDeleteRows(fate,hfate)

	def insertOrDeleteColumns(self,fate,wfate):
		return self.core.insertOrDeleteColumns(fate,wfate)

	def trimBlank(self):
		return self.core.trimBlank()

	def getData(self):
		return None

	def clone(self):
		return self.core.clone()

	def create(self):
		return self.t.create()

	def getMeta(self):
		return self.meta

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.t = None
		_hx_o.body = None
		_hx_o.head = None
		_hx_o.dx = None
		_hx_o.dy = None
		_hx_o.core = None
		_hx_o.meta = None


CombinedTable = _hx_classes.registerClass("CombinedTable", fields=["t","body","head","dx","dy","core","meta"], methods=["all","getTable","get_width","get_height","getCell","setCell","toString","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","getData","clone","create","getMeta"], interfaces=[Table])(CombinedTable)

class CombinedTableBody(object):

	def __init__(self,parent,dx,dy):
		self.parent = None
		self.dx = None
		self.dy = None
		self.all = None
		self.meta = None
		self.parent = parent
		self.dx = dx
		self.dy = dy
		self.all = parent.all()

	def getTable(self):
		return self

	def get_width(self):
		return (self.all.get_width() - 1)

	def get_height(self):
		return ((self.all.get_height() - self.dy) + 1)

	def getCell(self,x,y):
		if (y == 0):
			if (self.meta is None):
				self.meta = self.parent.getMeta().asTable()
			return self.meta.getCell((x + self.dx),0)
		return self.all.getCell((x + self.dx),((y + self.dy) - 1))

	def setCell(self,x,y,c):
		if (y == 0):
			self.all.setCell((x + self.dx),0,c)
			return
		self.all.setCell((x + self.dx),((y + self.dy) - 1),c)

	def toString(self):
		return SimpleTable.tableToString(self)

	def getCellView(self):
		return self.all.getCellView()

	def isResizable(self):
		return self.all.isResizable()

	def resize(self,w,h):
		return self.all.resize((w + 1),(h + self.dy))

	def clear(self):
		self.all.clear()
		self.dx = 0
		self.dy = 0

	def insertOrDeleteRows(self,fate,hfate):
		fate2 = list()
		_g1 = 0
		_g = self.dy
		while ((_g1 < _g)):
			y = _g1
			_g1 = (_g1 + 1)
			fate2.append(y)
			python_lib_Builtin.len(fate2)
		hdr = True
		_g2 = 0
		while ((_g2 < python_lib_Builtin.len(fate))):
			f = (fate[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(fate) else None)
			_g2 = (_g2 + 1)
			if hdr:
				hdr = False
				continue
			fate2.append((((f + self.dy) - 1) if ((f >= 0)) else f))
			python_lib_Builtin.len(fate2)
		return self.all.insertOrDeleteRows(fate2,((hfate + self.dy) - 1))

	def insertOrDeleteColumns(self,fate,wfate):
		fate2 = list()
		_g1 = 0
		_g = (self.dx + 1)
		while ((_g1 < _g)):
			x = _g1
			_g1 = (_g1 + 1)
			fate2.append(x)
			python_lib_Builtin.len(fate2)
		_g2 = 0
		while ((_g2 < python_lib_Builtin.len(fate))):
			f = (fate[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(fate) else None)
			_g2 = (_g2 + 1)
			fate2.append((((f + self.dx) + 1) if ((f >= 0)) else f))
			python_lib_Builtin.len(fate2)
		return self.all.insertOrDeleteColumns(fate2,(wfate + self.dx))

	def trimBlank(self):
		return self.all.trimBlank()

	def getData(self):
		return None

	def clone(self):
		return CombinedTable(self.all.clone())

	def create(self):
		return CombinedTable(self.all.create())

	def getMeta(self):
		return self.parent.getMeta()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.parent = None
		_hx_o.dx = None
		_hx_o.dy = None
		_hx_o.all = None
		_hx_o.meta = None


CombinedTableBody = _hx_classes.registerClass("CombinedTableBody", fields=["parent","dx","dy","all","meta"], methods=["getTable","get_width","get_height","getCell","setCell","toString","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","getData","clone","create","getMeta"], interfaces=[Table])(CombinedTableBody)

class CombinedTableHead(object):

	def __init__(self,parent,dx,dy):
		self.parent = None
		self.dx = None
		self.dy = None
		self.all = None
		self.parent = parent
		self.dx = dx
		self.dy = dy
		self.all = parent.all()

	def getTable(self):
		return self

	def get_width(self):
		return self.all.get_width()

	def get_height(self):
		return self.dy

	def getCell(self,x,y):
		if (x == 0):
			v = self.getCellView()
			txt = v.toString(self.all.getCell(x,y))
			if ((("" if ((0 >= python_lib_Builtin.len(txt))) else txt[0])) == "@"):
				return HxString.substr(txt,1,python_lib_Builtin.len(txt))
		return self.all.getCell(x,y)

	def setCell(self,x,y,c):
		self.all.setCell(x,y,c)

	def toString(self):
		return SimpleTable.tableToString(self)

	def getCellView(self):
		return self.all.getCellView()

	def isResizable(self):
		return False

	def resize(self,w,h):
		return False

	def clear(self):
		pass

	def insertOrDeleteRows(self,fate,hfate):
		return False

	def insertOrDeleteColumns(self,fate,wfate):
		return self.all.insertOrDeleteColumns(fate,wfate)

	def trimBlank(self):
		return False

	def getData(self):
		return None

	def clone(self):
		return None

	def create(self):
		return None

	def getMeta(self):
		return None

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.parent = None
		_hx_o.dx = None
		_hx_o.dy = None
		_hx_o.all = None


CombinedTableHead = _hx_classes.registerClass("CombinedTableHead", fields=["parent","dx","dy","all"], methods=["getTable","get_width","get_height","getCell","setCell","toString","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","getData","clone","create","getMeta"], interfaces=[Table])(CombinedTableHead)

class CompareFlags(object):

	def __init__(self):
		self.ordered = None
		self.show_unchanged = None
		self.unchanged_context = None
		self.always_show_order = None
		self.never_show_order = None
		self.show_unchanged_columns = None
		self.unchanged_column_context = None
		self.always_show_header = None
		self.acts = None
		self.ids = None
		self.columns_to_ignore = None
		self.tables = None
		self.allow_nested_cells = None
		self.warnings = None
		self.diff_strategy = None
		self.padding_strategy = None
		self.show_meta = None
		self.show_unchanged_meta = None
		self.parent = None
		self.count_like_a_spreadsheet = None
		self.ignore_whitespace = None
		self.ignore_case = None
		self.terminal_format = None
		self.ordered = True
		self.show_unchanged = False
		self.unchanged_context = 1
		self.always_show_order = False
		self.never_show_order = True
		self.show_unchanged_columns = False
		self.unchanged_column_context = 1
		self.always_show_header = True
		self.acts = None
		self.ids = None
		self.columns_to_ignore = None
		self.allow_nested_cells = False
		self.warnings = None
		self.diff_strategy = None
		self.show_meta = True
		self.show_unchanged_meta = False
		self.tables = None
		self.parent = None
		self.count_like_a_spreadsheet = True
		self.ignore_whitespace = False
		self.ignore_case = False
		self.terminal_format = None

	def filter(self,act,allow):
		if (self.acts is None):
			self.acts = haxe_ds_StringMap()
			self.acts.h["update"] = (not allow)
			self.acts.h["insert"] = (not allow)
			self.acts.h["delete"] = (not allow)
		if (not act in self.acts.h):
			return False
		self.acts.h[act] = allow
		return True

	def allowUpdate(self):
		if (self.acts is None):
			return True
		return "update" in self.acts.h

	def allowInsert(self):
		if (self.acts is None):
			return True
		return "insert" in self.acts.h

	def allowDelete(self):
		if (self.acts is None):
			return True
		return "delete" in self.acts.h

	def getIgnoredColumns(self):
		if (self.columns_to_ignore is None):
			return None
		ignore = haxe_ds_StringMap()
		_g1 = 0
		_g = python_lib_Builtin.len(self.columns_to_ignore)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ignore.h[(self.columns_to_ignore[i] if i >= 0 and i < python_lib_Builtin.len(self.columns_to_ignore) else None)] = True
		return ignore

	def addPrimaryKey(self,column):
		if (self.ids is None):
			self.ids = list()
		_this = self.ids
		_this.append(column)
		python_lib_Builtin.len(_this)

	def ignoreColumn(self,column):
		if (self.columns_to_ignore is None):
			self.columns_to_ignore = list()
		_this = self.columns_to_ignore
		_this.append(column)
		python_lib_Builtin.len(_this)

	def addTable(self,table):
		if (self.tables is None):
			self.tables = list()
		_this = self.tables
		_this.append(table)
		python_lib_Builtin.len(_this)

	def addWarning(self,warn):
		if (self.warnings is None):
			self.warnings = list()
		_this = self.warnings
		_this.append(warn)
		python_lib_Builtin.len(_this)

	def getWarning(self):
		return "\n".join([python_Boot.toString1(x1,'') for x1 in self.warnings])

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.ordered = None
		_hx_o.show_unchanged = None
		_hx_o.unchanged_context = None
		_hx_o.always_show_order = None
		_hx_o.never_show_order = None
		_hx_o.show_unchanged_columns = None
		_hx_o.unchanged_column_context = None
		_hx_o.always_show_header = None
		_hx_o.acts = None
		_hx_o.ids = None
		_hx_o.columns_to_ignore = None
		_hx_o.tables = None
		_hx_o.allow_nested_cells = None
		_hx_o.warnings = None
		_hx_o.diff_strategy = None
		_hx_o.padding_strategy = None
		_hx_o.show_meta = None
		_hx_o.show_unchanged_meta = None
		_hx_o.parent = None
		_hx_o.count_like_a_spreadsheet = None
		_hx_o.ignore_whitespace = None
		_hx_o.ignore_case = None
		_hx_o.terminal_format = None


CompareFlags = _hx_classes.registerClass("CompareFlags", fields=["ordered","show_unchanged","unchanged_context","always_show_order","never_show_order","show_unchanged_columns","unchanged_column_context","always_show_header","acts","ids","columns_to_ignore","tables","allow_nested_cells","warnings","diff_strategy","padding_strategy","show_meta","show_unchanged_meta","parent","count_like_a_spreadsheet","ignore_whitespace","ignore_case","terminal_format"], methods=["filter","allowUpdate","allowInsert","allowDelete","getIgnoredColumns","addPrimaryKey","ignoreColumn","addTable","addWarning","getWarning"])(CompareFlags)

class CompareTable(object):

	def __init__(self,comp):
		self.comp = None
		self.indexes = None
		self.comp = comp
		if (comp.compare_flags is not None):
			if (comp.compare_flags.parent is not None):
				comp.p = comp.compare_flags.parent

	def run(self):
		if self.useSql():
			self.comp.completed = True
			return False
		more = self.compareCore()
		while ((more and self.comp.run_to_completion)):
			more = self.compareCore()
		return (not more)

	def align(self):
		while ((not self.comp.completed)):
			self.run()
		alignment = Alignment()
		self.alignCore(alignment)
		alignment.comp = self.comp
		self.comp.alignment = alignment
		return alignment

	def getComparisonState(self):
		return self.comp

	def alignCore(self,align):
		if self.useSql():
			tab1 = None
			tab2 = None
			tab3 = None
			if (self.comp.p is None):
				tab1 = self.comp.a
				tab2 = self.comp.b
			else:
				align.reference = Alignment()
				tab1 = self.comp.p
				tab2 = self.comp.b
				tab3 = self.comp.a
			db = None
			if (tab1 is not None):
				db = tab1.getDatabase()
			if ((db is None) and ((tab2 is not None))):
				db = tab2.getDatabase()
			if ((db is None) and ((tab3 is not None))):
				db = tab3.getDatabase()
			sc = SqlCompare(db, tab1, tab2, tab3, align)
			sc.apply()
			if (self.comp.p is not None):
				align.meta.reference = align.reference.meta
			return
		if (self.comp.p is None):
			self.alignCore2(align,self.comp.a,self.comp.b)
			return
		align.reference = Alignment()
		self.alignCore2(align,self.comp.p,self.comp.b)
		self.alignCore2(align.reference,self.comp.p,self.comp.a)
		align.meta.reference = align.reference.meta

	def alignCore2(self,align,a,b):
		if (align.meta is None):
			align.meta = Alignment()
		self.alignColumns(align.meta,a,b)
		column_order = align.meta.toOrder()
		align.range(a.get_height(),b.get_height())
		align.tables(a,b)
		align.setRowlike(True)
		w = a.get_width()
		ha = a.get_height()
		hb = b.get_height()
		av = a.getCellView()
		ids = None
		ignore = None
		if (self.comp.compare_flags is not None):
			ids = self.comp.compare_flags.ids
			ignore = self.comp.compare_flags.getIgnoredColumns()
		common_units = list()
		ra_header = align.getSourceHeader()
		rb_header = align.getSourceHeader()
		_g = 0
		_g1 = column_order.getList()
		while ((_g < python_lib_Builtin.len(_g1))):
			unit = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (((unit.l >= 0) and ((unit.r >= 0))) and ((unit.p != -1))):
				if (ignore is not None):
					if (((unit.l >= 0) and ((ra_header >= 0))) and ((ra_header < a.get_height()))):
						name = av.toString(a.getCell(unit.l,ra_header))
						if name in ignore.h:
							continue
					if (((unit.r >= 0) and ((rb_header >= 0))) and ((rb_header < b.get_height()))):
						name1 = av.toString(b.getCell(unit.r,rb_header))
						if name1 in ignore.h:
							continue
				common_units.append(unit)
				python_lib_Builtin.len(common_units)
		index_top = None
		pending_ct = ha
		reverse_pending_ct = hb
		used = haxe_ds_IntMap()
		used_reverse = haxe_ds_IntMap()
		if (ids is not None):
			index_top = IndexPair(self.comp.compare_flags)
			ids_as_map = haxe_ds_StringMap()
			_g2 = 0
			while ((_g2 < python_lib_Builtin.len(ids))):
				id = (ids[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(ids) else None)
				_g2 = (_g2 + 1)
				ids_as_map.h[id] = True
				True
			_g3 = 0
			while ((_g3 < python_lib_Builtin.len(common_units))):
				unit1 = (common_units[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(common_units) else None)
				_g3 = (_g3 + 1)
				na = av.toString(a.getCell(unit1.l,0))
				nb = av.toString(b.getCell(unit1.r,0))
				if (na in ids_as_map.h or nb in ids_as_map.h):
					index_top.addColumns(unit1.l,unit1.r)
					align.addIndexColumns(unit1)
			index_top.indexTables(a,b,1)
			if (self.indexes is not None):
				_this = self.indexes
				_this.append(index_top)
				python_lib_Builtin.len(_this)
			_g4 = 0
			while ((_g4 < ha)):
				j = _g4
				_g4 = (_g4 + 1)
				cross = index_top.queryLocal(j)
				spot_a = cross.spot_a
				spot_b = cross.spot_b
				if ((spot_a != 1) or ((spot_b != 1))):
					continue
				jb = python_internal_ArrayImpl._get(cross.item_b.lst, 0)
				align.link(j,jb)
				used.set(jb,1)
				if (not j in used_reverse.h):
					reverse_pending_ct = (reverse_pending_ct - 1)
				used_reverse.set(j,1)
		else:
			N = 5
			columns = list()
			if (python_lib_Builtin.len(common_units) > N):
				columns_eval = list()
				_g11 = 0
				_g5 = python_lib_Builtin.len(common_units)
				while ((_g11 < _g5)):
					i = _g11
					_g11 = (_g11 + 1)
					ct = 0
					mem = haxe_ds_StringMap()
					mem2 = haxe_ds_StringMap()
					ca = (common_units[i] if i >= 0 and i < python_lib_Builtin.len(common_units) else None).l
					cb = (common_units[i] if i >= 0 and i < python_lib_Builtin.len(common_units) else None).r
					_g21 = 0
					while ((_g21 < ha)):
						j1 = _g21
						_g21 = (_g21 + 1)
						key = av.toString(a.getCell(ca,j1))
						if (not key in mem.h):
							mem.h[key] = 1
							ct = (ct + 1)
					_g22 = 0
					while ((_g22 < hb)):
						j2 = _g22
						_g22 = (_g22 + 1)
						key1 = av.toString(b.getCell(cb,j2))
						if (not key1 in mem2.h):
							mem2.h[key1] = 1
							ct = (ct + 1)
					columns_eval.append([i, ct])
					python_lib_Builtin.len(columns_eval)
				def _hx_local_6(a1,b1):
					if ((a1[1] if 1 < python_lib_Builtin.len(a1) else None) < (b1[1] if 1 < python_lib_Builtin.len(b1) else None)):
						return 1
					if ((a1[1] if 1 < python_lib_Builtin.len(a1) else None) > (b1[1] if 1 < python_lib_Builtin.len(b1) else None)):
						return -1
					if ((a1[0] if 0 < python_lib_Builtin.len(a1) else None) > (b1[0] if 0 < python_lib_Builtin.len(b1) else None)):
						return 1
					if ((a1[0] if 0 < python_lib_Builtin.len(a1) else None) < (b1[0] if 0 < python_lib_Builtin.len(b1) else None)):
						return -1
					return 0
				sorter = _hx_local_6
				columns_eval.sort(key= hx_cmp_to_key(sorter))
				def _hx_local_7(v):
					return (v[0] if 0 < python_lib_Builtin.len(v) else None)
				columns = Lambda.array(Lambda.map(columns_eval,_hx_local_7))
				columns = columns[0:N]
			else:
				_g12 = 0
				_g6 = python_lib_Builtin.len(common_units)
				while ((_g12 < _g6)):
					i1 = _g12
					_g12 = (_g12 + 1)
					columns.append(i1)
					python_lib_Builtin.len(columns)
			top = None
			v1 = Math.pow(2,python_lib_Builtin.len(columns))
			top = Math.floor((v1 + 0.5))
			pending = haxe_ds_IntMap()
			_g7 = 0
			while ((_g7 < ha)):
				j3 = _g7
				_g7 = (_g7 + 1)
				pending.set(j3,j3)
			added_columns = haxe_ds_IntMap()
			index_ct = 0
			_g8 = 0
			while ((_g8 < top)):
				k = _g8
				_g8 = (_g8 + 1)
				if (k == 0):
					continue
				if (pending_ct == 0):
					break
				active_columns = list()
				kk = k
				at = 0
				while ((kk > 0)):
					if ((kk % 2) == 1):
						active_columns.append((columns[at] if at >= 0 and at < python_lib_Builtin.len(columns) else None))
						python_lib_Builtin.len(active_columns)
					kk = (kk >> 1)
					at = (at + 1)
				index = IndexPair(self.comp.compare_flags)
				_g23 = 0
				_g13 = python_lib_Builtin.len(active_columns)
				while ((_g23 < _g13)):
					k1 = _g23
					_g23 = (_g23 + 1)
					col = (active_columns[k1] if k1 >= 0 and k1 < python_lib_Builtin.len(active_columns) else None)
					unit2 = (common_units[col] if col >= 0 and col < python_lib_Builtin.len(common_units) else None)
					index.addColumns(unit2.l,unit2.r)
					if (not col in added_columns.h):
						align.addIndexColumns(unit2)
						added_columns.set(col,True)
				index.indexTables(a,b,1)
				if (k == ((top - 1))):
					index_top = index
				h = a.get_height()
				if (b.get_height() > h):
					h = b.get_height()
				if (h < 1):
					h = 1
				wide_top_freq = index.getTopFreq()
				ratio = wide_top_freq
				ratio = (ratio / ((h + 20)))
				if (ratio >= 0.1):
					if ((index_ct > 0) or ((k < ((top - 1))))):
						continue
				index_ct = (index_ct + 1)
				if (self.indexes is not None):
					_this1 = self.indexes
					_this1.append(index)
					python_lib_Builtin.len(_this1)
				fixed = list()
				_hx_local_13 = pending.keys()
				while (_hx_local_13.hasNext()):
					j4 = hxnext(_hx_local_13)
					cross1 = index.queryLocal(j4)
					spot_a1 = cross1.spot_a
					spot_b1 = cross1.spot_b
					if ((spot_a1 != 1) or ((spot_b1 != 1))):
						continue
					val = python_internal_ArrayImpl._get(cross1.item_b.lst, 0)
					if (not val in used.h):
						fixed.append(j4)
						python_lib_Builtin.len(fixed)
						align.link(j4,val)
						used.set(val,1)
						if (not j4 in used_reverse.h):
							reverse_pending_ct = (reverse_pending_ct - 1)
						used_reverse.set(j4,1)
				_g24 = 0
				_g14 = python_lib_Builtin.len(fixed)
				while ((_g24 < _g14)):
					j5 = _g24
					_g24 = (_g24 + 1)
					pending.remove((fixed[j5] if j5 >= 0 and j5 < python_lib_Builtin.len(fixed) else None))
					pending_ct = (pending_ct - 1)
		if (index_top is not None):
			offset = 0
			scale = 1
			_g9 = 0
			while ((_g9 < 2)):
				sgn = _g9
				_g9 = (_g9 + 1)
				if (pending_ct > 0):
					xb = None
					if ((scale == -1) and ((hb > 0))):
						xb = (hb - 1)
					_g15 = 0
					while ((_g15 < ha)):
						xa0 = _g15
						_g15 = (_g15 + 1)
						xa = ((xa0 * scale) + offset)
						xb2 = align.a2b(xa)
						if (xb2 is not None):
							xb = (xb2 + scale)
							if ((xb >= hb) or ((xb < 0))):
								break
							continue
						if (xb is None):
							continue
						ka = index_top.localKey(xa)
						kb = index_top.remoteKey(xb)
						if (ka != kb):
							continue
						if xb in used.h:
							continue
						align.link(xa,xb)
						used.set(xb,1)
						used_reverse.set(xa,1)
						pending_ct = (pending_ct - 1)
						xb = (xb + scale)
						if ((xb >= hb) or ((xb < 0))):
							break
						if (pending_ct == 0):
							break
				offset = (ha - 1)
				scale = -1
			offset = 0
			scale = 1
			_g10 = 0
			while ((_g10 < 2)):
				sgn1 = _g10
				_g10 = (_g10 + 1)
				if (reverse_pending_ct > 0):
					xa1 = None
					if ((scale == -1) and ((ha > 0))):
						xa1 = (ha - 1)
					_g16 = 0
					while ((_g16 < hb)):
						xb0 = _g16
						_g16 = (_g16 + 1)
						xb1 = ((xb0 * scale) + offset)
						xa2 = align.b2a(xb1)
						if (xa2 is not None):
							xa1 = (xa2 + scale)
							if ((xa1 >= ha) or ((xa1 < 0))):
								break
							continue
						if (xa1 is None):
							continue
						ka1 = index_top.localKey(xa1)
						kb1 = index_top.remoteKey(xb1)
						if (ka1 != kb1):
							continue
						if xa1 in used_reverse.h:
							continue
						align.link(xa1,xb1)
						used.set(xb1,1)
						used_reverse.set(xa1,1)
						reverse_pending_ct = (reverse_pending_ct - 1)
						xa1 = (xa1 + scale)
						if ((xa1 >= ha) or ((xa1 < 0))):
							break
						if (reverse_pending_ct == 0):
							break
				offset = (hb - 1)
				scale = -1
		_g17 = 1
		while ((_g17 < ha)):
			i2 = _g17
			_g17 = (_g17 + 1)
			if (not i2 in used_reverse.h):
				align.link(i2,-1)
		_g18 = 1
		while ((_g18 < hb)):
			i3 = _g18
			_g18 = (_g18 + 1)
			if (not i3 in used.h):
				align.link(-1,i3)
		if ((ha > 0) and ((hb > 0))):
			align.link(0,0)

	def alignColumns(self,align,a,b):
		align.range(a.get_width(),b.get_width())
		align.tables(a,b)
		align.setRowlike(False)
		slop = 5
		va = a.getCellView()
		vb = b.getCellView()
		ra_best = 0
		rb_best = 0
		ct_best = -1
		ma_best = None
		mb_best = None
		ra_header = 0
		rb_header = 0
		ra_uniques = 0
		rb_uniques = 0
		_g = 0
		while ((_g < slop)):
			ra = _g
			_g = (_g + 1)
			_g1 = 0
			while ((_g1 < slop)):
				rb = _g1
				_g1 = (_g1 + 1)
				ma = haxe_ds_StringMap()
				mb = haxe_ds_StringMap()
				ct = 0
				uniques = 0
				if (ra < a.get_height()):
					_g3 = 0
					_g2 = a.get_width()
					while ((_g3 < _g2)):
						ca = _g3
						_g3 = (_g3 + 1)
						key = va.toString(a.getCell(ca,ra))
						if key in ma.h:
							ma.h[key] = -1
							uniques = (uniques - 1)
						else:
							ma.h[key] = ca
							uniques = (uniques + 1)
					if (uniques > ra_uniques):
						ra_header = ra
						ra_uniques = uniques
				uniques = 0
				if (rb < b.get_height()):
					_g31 = 0
					_g21 = b.get_width()
					while ((_g31 < _g21)):
						cb = _g31
						_g31 = (_g31 + 1)
						key1 = vb.toString(b.getCell(cb,rb))
						if key1 in mb.h:
							mb.h[key1] = -1
							uniques = (uniques - 1)
						else:
							mb.h[key1] = cb
							uniques = (uniques + 1)
					if (uniques > rb_uniques):
						rb_header = rb
						rb_uniques = uniques
				_hx_local_5 = ma.keys()
				while (_hx_local_5.hasNext()):
					key2 = hxnext(_hx_local_5)
					i0 = ma.h.get(key2,None)
					i1 = mb.h.get(key2,None)
					if (i1 is not None):
						if ((i1 >= 0) and ((i0 >= 0))):
							ct = (ct + 1)
				if (ct > ct_best):
					ct_best = ct
					ma_best = ma
					mb_best = mb
					ra_best = ra
					rb_best = rb
		if (ma_best is None):
			if ((a.get_height() > 0) and ((b.get_height() == 0))):
				align.headers(0,-1)
			elif ((a.get_height() == 0) and ((b.get_height() > 0))):
				align.headers(-1,0)
			return
		_hx_local_6 = ma_best.keys()
		while (_hx_local_6.hasNext()):
			key3 = hxnext(_hx_local_6)
			i01 = ma_best.h.get(key3,None)
			i11 = mb_best.h.get(key3,None)
			if ((i01 is not None) and ((i11 is not None))):
				align.link(i01,i11)
			elif (i01 is not None):
				align.link(i01,-1)
			elif (i11 is not None):
				align.link(-1,i11)
		_hx_local_7 = mb_best.keys()
		while (_hx_local_7.hasNext()):
			key4 = hxnext(_hx_local_7)
			i02 = ma_best.h.get(key4,None)
			i12 = mb_best.h.get(key4,None)
			if ((i02 is None) and ((i12 is not None))):
				align.link(-1,i12)
		align.headers(ra_header,rb_header)

	def testHasSameColumns(self):
		p = self.comp.p
		a = self.comp.a
		b = self.comp.b
		eq = self.hasSameColumns2(a,b)
		if (eq and ((p is not None))):
			eq = self.hasSameColumns2(p,a)
		self.comp.has_same_columns = eq
		self.comp.has_same_columns_known = True
		return True

	def hasSameColumns2(self,a,b):
		if (a.get_width() != b.get_width()):
			return False
		if ((a.get_height() == 0) or ((b.get_height() == 0))):
			return True
		av = a.getCellView()
		_g1 = 0
		_g = a.get_width()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = (i + 1)
			_g2 = a.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				if av.equals(a.getCell(i,0),a.getCell(j,0)):
					return False
			if (not av.equals(a.getCell(i,0),b.getCell(i,0))):
				return False
		return True

	def testIsEqual(self):
		p = self.comp.p
		a = self.comp.a
		b = self.comp.b
		self.comp.getMeta()
		nested = False
		if (self.comp.p_meta is not None):
			if self.comp.p_meta.isNested():
				nested = True
		if (self.comp.a_meta is not None):
			if self.comp.a_meta.isNested():
				nested = True
		if (self.comp.b_meta is not None):
			if self.comp.b_meta.isNested():
				nested = True
		if nested:
			self.comp.is_equal = False
			self.comp.is_equal_known = True
			return True
		eq = self.isEqual2(a,b)
		if (eq and ((p is not None))):
			eq = self.isEqual2(p,a)
		self.comp.is_equal = eq
		self.comp.is_equal_known = True
		return True

	def isEqual2(self,a,b):
		if ((a.get_width() != b.get_width()) or ((a.get_height() != b.get_height()))):
			return False
		av = a.getCellView()
		_g1 = 0
		_g = a.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = 0
			_g2 = a.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				if (not av.equals(a.getCell(j,i),b.getCell(j,i))):
					return False
		return True

	def compareCore(self):
		if self.comp.completed:
			return False
		if (not self.comp.is_equal_known):
			return self.testIsEqual()
		if (not self.comp.has_same_columns_known):
			return self.testHasSameColumns()
		self.comp.completed = True
		return False

	def storeIndexes(self):
		self.indexes = list()

	def getIndexes(self):
		return self.indexes

	def useSql(self):
		if (self.comp.compare_flags is None):
			return False
		self.comp.getMeta()
		sql = True
		if (self.comp.p_meta is not None):
			if (not self.comp.p_meta.isSql()):
				sql = False
		if (self.comp.a_meta is not None):
			if (not self.comp.a_meta.isSql()):
				sql = False
		if (self.comp.b_meta is not None):
			if (not self.comp.b_meta.isSql()):
				sql = False
		if ((self.comp.p is not None) and ((self.comp.p_meta is None))):
			sql = False
		if ((self.comp.a is not None) and ((self.comp.a_meta is None))):
			sql = False
		if ((self.comp.b is not None) and ((self.comp.b_meta is None))):
			sql = False
		return sql

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.comp = None
		_hx_o.indexes = None


CompareTable = _hx_classes.registerClass("CompareTable", fields=["comp","indexes"], methods=["run","align","getComparisonState","alignCore","alignCore2","alignColumns","testHasSameColumns","hasSameColumns2","testIsEqual","isEqual2","compareCore","storeIndexes","getIndexes","useSql"])(CompareTable)

class Coopy(object):

	def __init__(self,io = None):
		self.format_preference = None
		self.delim_preference = None
		self.extern_preference = None
		self.output_format = None
		self.output_format_set = None
		self.nested_output = None
		self.order_set = None
		self.order_preference = None
		self.io = None
		self.pretty = None
		self.strategy = None
		self.css_output = None
		self.fragment = None
		self.flags = None
		self.cache_txt = None
		self.mv = None
		self.status = None
		self.daff_cmd = None
		self.init()
		self.io = io

	def init(self):
		self.extern_preference = False
		self.format_preference = None
		self.delim_preference = None
		self.output_format = "copy"
		self.output_format_set = False
		self.nested_output = False
		self.order_set = False
		self.order_preference = False
		self.strategy = None
		self.pretty = True
		self.css_output = None
		self.fragment = False
		self.flags = None
		self.cache_txt = None

	def checkFormat(self,name):
		if self.extern_preference:
			return self.format_preference
		ext = ""
		if (name is not None):
			pt = name.rfind(".", 0, python_lib_Builtin.len(name))
			if (pt >= 0):
				_this = HxString.substr(name,(pt + 1),None)
				ext = _this.lower()
				_hx_local_0 = python_lib_Builtin.len((ext))
				if (_hx_local_0 == 4):
					if ((ext) == "json"):
						self.format_preference = "json"
					elif ((ext) == "html"):
						self.format_preference = "html"
					else:
						ext = ""
				elif (_hx_local_0 == 3):
					if ((ext) == "csv"):
						self.format_preference = "csv"
						self.delim_preference = ","
					elif ((ext) == "tsv"):
						self.format_preference = "csv"
						self.delim_preference = "\t"
					elif ((ext) == "ssv"):
						self.format_preference = "csv"
						self.delim_preference = ";"
					elif ((ext) == "htm"):
						self.format_preference = "html"
					elif ((ext) == "www"):
						self.format_preference = "www"
					else:
						ext = ""
				elif (_hx_local_0 == 7):
					if ((ext) == "sqlite3"):
						self.format_preference = "sqlite"
					else:
						ext = ""
				elif (_hx_local_0 == 6):
					if ((ext) == "ndjson"):
						self.format_preference = "ndjson"
					elif ((ext) == "sqlite"):
						self.format_preference = "sqlite"
					else:
						ext = ""
				else:
					ext = ""
		self.nested_output = ((self.format_preference == "json") or ((self.format_preference == "ndjson")))
		self.order_preference = (not self.nested_output)
		return ext

	def setFormat(self,name):
		self.extern_preference = False
		self.checkFormat(("." + HxOverrides.stringOrNull(name)))
		self.extern_preference = True

	def getRenderer(self):
		renderer = DiffRender()
		renderer.usePrettyArrows(self.pretty)
		return renderer

	def applyRenderer(self,name,renderer):
		if (not self.fragment):
			renderer.completeHtml()
		if (self.format_preference == "www"):
			self.io.sendToBrowser(renderer.html())
		else:
			self.saveText(name,renderer.html())
		if (self.css_output is not None):
			self.saveText(self.css_output,renderer.sampleCss())
		return True

	def renderTable(self,name,t):
		renderer = self.getRenderer()
		renderer.render(t)
		return self.applyRenderer(name,renderer)

	def renderTables(self,name,t):
		renderer = self.getRenderer()
		renderer.renderTables(t)
		return self.applyRenderer(name,renderer)

	def saveTable(self,name,t,render = None):
		txt = self.encodeTable(name,t,render)
		if (txt is None):
			return True
		return self.saveText(name,txt)

	def encodeTable(self,name,t,render = None):
		if (self.output_format != "copy"):
			self.setFormat(self.output_format)
		txt = ""
		self.checkFormat(name)
		if ((self.format_preference == "sqlite") and (not self.extern_preference)):
			self.format_preference = "csv"
		if (render is None):
			if (self.format_preference == "csv"):
				csv = Csv(self.delim_preference)
				txt = csv.renderTable(t)
			elif (self.format_preference == "ndjson"):
				txt = Ndjson(t).render()
			elif ((self.format_preference == "html") or ((self.format_preference == "www"))):
				self.renderTable(name,t)
				return None
			elif (self.format_preference == "sqlite"):
				self.io.writeStderr("! Cannot yet output to sqlite, aborting\n")
				return ""
			else:
				value = Coopy.jsonify(t)
				txt = haxe_format_JsonPrinter._hx_print(value,None,"  ")
		else:
			txt = render.render(t)
		return txt

	def saveTables(self,name,os,use_color):
		if (self.output_format != "copy"):
			self.setFormat(self.output_format)
		txt = ""
		self.checkFormat(name)
		render = None
		if use_color:
			render = TerminalDiffRender(self.flags)
		order = os.getOrder()
		if (python_lib_Builtin.len(order) == 1):
			return self.saveTable(name,os.one(),render)
		if ((self.format_preference == "html") or ((self.format_preference == "www"))):
			return self.renderTables(name,os)
		need_blank = False
		if ((python_lib_Builtin.len(order) == 0) or os.hasInsDel()):
			txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.encodeTable(name,os.one(),render)))
			need_blank = True
		if (python_lib_Builtin.len(order) > 1):
			_g1 = 1
			_g = python_lib_Builtin.len(order)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				t = os.get((order[i] if i >= 0 and i < python_lib_Builtin.len(order) else None))
				if (t is not None):
					if need_blank:
						txt = (HxOverrides.stringOrNull(txt) + "\n")
					need_blank = True
					txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull((order[i] if i >= 0 and i < python_lib_Builtin.len(order) else None)) + "\n"))))
					line = ""
					_g3 = 0
					_g2 = python_lib_Builtin.len((order[i] if i >= 0 and i < python_lib_Builtin.len(order) else None))
					while ((_g3 < _g2)):
						i1 = _g3
						_g3 = (_g3 + 1)
						line = (HxOverrides.stringOrNull(line) + "=")
					txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull(line) + "\n"))))
					txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.encodeTable(name,os.get((order[i] if i >= 0 and i < python_lib_Builtin.len(order) else None)),render)))
		return self.saveText(name,txt)

	def saveText(self,name,txt):
		if (name is None):
			_hx_local_0 = self
			_hx_local_1 = _hx_local_0.cache_txt
			_hx_local_0.cache_txt = (HxOverrides.stringOrNull(_hx_local_1) + HxOverrides.stringOrNull(txt))
			_hx_local_0.cache_txt
		elif (name != "-"):
			self.io.saveContent(name,txt)
		else:
			self.io.writeStdout(txt)
		return True

	def jsonToTables(self,json):
		tables = python_Boot.field(json,"tables")
		if (tables is None):
			return self.jsonToTable(json)
		return JsonTables(json, self.flags)

	def jsonToTable(self,json):
		output = None
		_g = 0
		_g1 = python_Boot.fields(json)
		while ((_g < python_lib_Builtin.len(_g1))):
			name = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			t = python_Boot.field(json,name)
			columns = python_Boot.field(t,"columns")
			if (columns is None):
				continue
			rows = python_Boot.field(t,"rows")
			if (rows is None):
				continue
			output = SimpleTable(python_lib_Builtin.len(columns), python_lib_Builtin.len(rows))
			has_hash = False
			has_hash_known = False
			_g3 = 0
			_g2 = python_lib_Builtin.len(rows)
			while ((_g3 < _g2)):
				i = _g3
				_g3 = (_g3 + 1)
				row = (rows[i] if i >= 0 and i < python_lib_Builtin.len(rows) else None)
				if (not has_hash_known):
					if (python_lib_Builtin.len(python_Boot.fields(row)) == python_lib_Builtin.len(columns)):
						has_hash = True
					has_hash_known = True
				if (not has_hash):
					lst = row
					_g5 = 0
					_g4 = python_lib_Builtin.len(columns)
					while ((_g5 < _g4)):
						j = _g5
						_g5 = (_g5 + 1)
						val = (lst[j] if j >= 0 and j < python_lib_Builtin.len(lst) else None)
						output.setCell(j,i,Coopy.cellFor(val))
				else:
					_g51 = 0
					_g41 = python_lib_Builtin.len(columns)
					while ((_g51 < _g41)):
						j1 = _g51
						_g51 = (_g51 + 1)
						val1 = python_Boot.field(row,(columns[j1] if j1 >= 0 and j1 < python_lib_Builtin.len(columns) else None))
						output.setCell(j1,i,Coopy.cellFor(val1))
		if (output is not None):
			output.trimBlank()
		return output

	def runDiff(self,parent,a,b,flags,output):
		ct = Coopy.compareTables3(parent,a,b,flags)
		align = ct.align()
		td = TableDiff(align, flags)
		o = SimpleTable(0, 0)
		os = Tables(o)
		td.hiliteWithNesting(os)
		use_color = (flags.terminal_format == "ansi")
		if (flags.terminal_format is None):
			if ((((output is None) or ((output == "-")))) and (((self.output_format == "copy") or ((self.output_format == "csv"))))):
				if (self.io is not None):
					if self.io.isTtyKnown():
						use_color = self.io.isTty()
		self.saveTables(output,os,use_color)

	def loadTable(self,name):
		ext = self.checkFormat(name)
		if (ext == "sqlite"):
			sql = self.io.openSqliteDatabase(name)
			if (sql is None):
				self.io.writeStderr("! Cannot open database, aborting\n")
				return None
			tab = SqlTables(sql, self.flags)
			return tab
		txt = self.io.getContent(name)
		if (ext == "ndjson"):
			t = SimpleTable(0, 0)
			ndjson = Ndjson(t)
			ndjson.parse(txt)
			return t
		if ((ext == "json") or ((ext == ""))):
			try:
				json = python_lib_Json.loads(txt,None,None,python_Lib.dictToAnon)
				self.format_preference = "json"
				t1 = self.jsonToTables(json)
				if (t1 is None):
					raise _HxException("JSON failed")
				return t1
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e = _hx_e1
				if (ext == "json"):
					raise _HxException(e)
		self.format_preference = "csv"
		csv = Csv(self.delim_preference)
		output = SimpleTable(0, 0)
		csv.parseTable(txt,output)
		if (output is not None):
			output.trimBlank()
		return output

	def command(self,io,cmd,args):
		r = 0
		if io.async():
			r = io.command(cmd,args)
		if (r != 999):
			io.writeStdout(("$ " + HxOverrides.stringOrNull(cmd)))
			_g = 0
			while ((_g < python_lib_Builtin.len(args))):
				arg = (args[_g] if _g >= 0 and _g < python_lib_Builtin.len(args) else None)
				_g = (_g + 1)
				io.writeStdout(" ")
				spaced = (arg.find(" ") >= 0)
				if spaced:
					io.writeStdout("\"")
				io.writeStdout(arg)
				if spaced:
					io.writeStdout("\"")
			io.writeStdout("\n")
		if (not io.async()):
			r = io.command(cmd,args)
		return r

	def installGitDriver(self,io,formats):
		r = 0
		if (self.status is None):
			self.status = haxe_ds_StringMap()
			self.daff_cmd = ""
		key = "hello"
		if (not key in self.status.h):
			io.writeStdout("Setting up git to use daff on")
			_g = 0
			while ((_g < python_lib_Builtin.len(formats))):
				format = (formats[_g] if _g >= 0 and _g < python_lib_Builtin.len(formats) else None)
				_g = (_g + 1)
				io.writeStdout((" *." + HxOverrides.stringOrNull(format)))
			io.writeStdout(" files\n")
			self.status.h[key] = r
		key = "can_run_git"
		if (not key in self.status.h):
			r = self.command(io,"git",["--version"])
			if (r == 999):
				return r
			self.status.h[key] = r
			if (r != 0):
				io.writeStderr("! Cannot run git, aborting\n")
				return 1
			io.writeStdout("- Can run git\n")
		daffs = ["daff", "daff.rb", "daff.py"]
		if (self.daff_cmd == ""):
			_g1 = 0
			while ((_g1 < python_lib_Builtin.len(daffs))):
				daff = (daffs[_g1] if _g1 >= 0 and _g1 < python_lib_Builtin.len(daffs) else None)
				_g1 = (_g1 + 1)
				key1 = ("can_run_" + HxOverrides.stringOrNull(daff))
				if (not key1 in self.status.h):
					r = self.command(io,daff,["version"])
					if (r == 999):
						return r
					self.status.h[key1] = r
					if (r == 0):
						self.daff_cmd = daff
						io.writeStdout((((("- Can run " + HxOverrides.stringOrNull(daff)) + " as \"") + HxOverrides.stringOrNull(daff)) + "\"\n"))
						break
			if (self.daff_cmd == ""):
				io.writeStderr("! Cannot find daff, is it in your path?\n")
				return 1
		_g2 = 0
		while ((_g2 < python_lib_Builtin.len(formats))):
			format1 = (formats[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(formats) else None)
			_g2 = (_g2 + 1)
			key = ("have_diff_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				r = self.command(io,"git",["config", "--global", "--get", (("diff.daff-" + HxOverrides.stringOrNull(format1)) + ".command")])
				if (r == 999):
					return r
				self.status.h[key] = r
			have_diff_driver = (self.status.h.get(key,None) == 0)
			key = ("add_diff_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				r = self.command(io,"git",["config", "--global", (("diff.daff-" + HxOverrides.stringOrNull(format1)) + ".command"), (HxOverrides.stringOrNull(self.daff_cmd) + " diff --git")])
				if (r == 999):
					return r
				if have_diff_driver:
					io.writeStdout((("- Cleared existing daff diff driver for " + HxOverrides.stringOrNull(format1)) + "\n"))
				io.writeStdout((("- Added diff driver for " + HxOverrides.stringOrNull(format1)) + "\n"))
				self.status.h[key] = r
			key = ("have_merge_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				r = self.command(io,"git",["config", "--global", "--get", (("merge.daff-" + HxOverrides.stringOrNull(format1)) + ".driver")])
				if (r == 999):
					return r
				self.status.h[key] = r
			have_merge_driver = (self.status.h.get(key,None) == 0)
			key = ("name_merge_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				if (not have_merge_driver):
					r = self.command(io,"git",["config", "--global", (("merge.daff-" + HxOverrides.stringOrNull(format1)) + ".name"), (("daff tabular " + HxOverrides.stringOrNull(format1)) + " merge")])
					if (r == 999):
						return r
				else:
					r = 0
				self.status.h[key] = r
			key = ("add_merge_driver_" + HxOverrides.stringOrNull(format1))
			if (not key in self.status.h):
				r = self.command(io,"git",["config", "--global", (("merge.daff-" + HxOverrides.stringOrNull(format1)) + ".driver"), (HxOverrides.stringOrNull(self.daff_cmd) + " merge --output %A %O %A %B")])
				if (r == 999):
					return r
				if have_merge_driver:
					io.writeStdout((("- Cleared existing daff merge driver for " + HxOverrides.stringOrNull(format1)) + "\n"))
				io.writeStdout((("- Added merge driver for " + HxOverrides.stringOrNull(format1)) + "\n"))
				self.status.h[key] = r
		if (not io.exists(".git/config")):
			io.writeStderr("! This next part needs to happen in a git repository.\n")
			io.writeStderr("! Please run again from the root of a git repository.\n")
			return 1
		attr = ".gitattributes"
		txt = ""
		post = ""
		if (not io.exists(attr)):
			io.writeStdout("- No .gitattributes file\n")
		else:
			io.writeStdout("- You have a .gitattributes file\n")
			txt = io.getContent(attr)
		need_update = False
		_g3 = 0
		while ((_g3 < python_lib_Builtin.len(formats))):
			format2 = (formats[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(formats) else None)
			_g3 = (_g3 + 1)
			def _hx_local_4():
				unicode = ("*." + HxOverrides.stringOrNull(format2))
				return txt.find(unicode)
			if (_hx_local_4() >= 0):
				io.writeStderr((("- Your .gitattributes file already mentions *." + HxOverrides.stringOrNull(format2)) + "\n"))
			else:
				post = (HxOverrides.stringOrNull(post) + HxOverrides.stringOrNull(((((("*." + HxOverrides.stringOrNull(format2)) + " diff=daff-") + HxOverrides.stringOrNull(format2)) + "\n"))))
				post = (HxOverrides.stringOrNull(post) + HxOverrides.stringOrNull(((((("*." + HxOverrides.stringOrNull(format2)) + " merge=daff-") + HxOverrides.stringOrNull(format2)) + "\n"))))
				io.writeStdout("- Placing the following lines in .gitattributes:\n")
				io.writeStdout(post)
				if ((txt != "") and (not need_update)):
					txt = (HxOverrides.stringOrNull(txt) + "\n")
				txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(post))
				need_update = True
		if need_update:
			io.saveContent(attr,txt)
		io.writeStdout("- Done!\n")
		return 0

	def run(self,args,io = None):
		if (io is None):
			io = TableIO()
		if (io is None):
			haxe_Log.trace("No system interface available",_hx_AnonObject({'fileName': "Coopy.hx", 'lineNumber': 695, 'className': "Coopy", 'methodName': "run"}))
			return 1
		self.init()
		self.io = io
		more = True
		output = None
		inplace = False
		git = False
		self.flags = CompareFlags()
		self.flags.always_show_header = True
		while (more):
			more = False
			_g1 = 0
			_g = python_lib_Builtin.len(args)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				tag = (args[i] if i >= 0 and i < python_lib_Builtin.len(args) else None)
				if (tag == "--output"):
					more = True
					output = python_internal_ArrayImpl._get(args, (i + 1))
					pos = i
					if (pos < 0):
						pos = (python_lib_Builtin.len(args) + pos)
					if (pos < 0):
						pos = 0
					res = args[pos:(pos + 2)]
					del args[pos:(pos + 2)]
					res
					break
				elif (tag == "--css"):
					more = True
					self.fragment = True
					self.css_output = python_internal_ArrayImpl._get(args, (i + 1))
					pos1 = i
					if (pos1 < 0):
						pos1 = (python_lib_Builtin.len(args) + pos1)
					if (pos1 < 0):
						pos1 = 0
					res1 = args[pos1:(pos1 + 2)]
					del args[pos1:(pos1 + 2)]
					res1
					break
				elif (tag == "--fragment"):
					more = True
					self.fragment = True
					pos2 = i
					if (pos2 < 0):
						pos2 = (python_lib_Builtin.len(args) + pos2)
					if (pos2 < 0):
						pos2 = 0
					res2 = args[pos2:(pos2 + 1)]
					del args[pos2:(pos2 + 1)]
					res2
					break
				elif (tag == "--plain"):
					more = True
					self.pretty = False
					pos3 = i
					if (pos3 < 0):
						pos3 = (python_lib_Builtin.len(args) + pos3)
					if (pos3 < 0):
						pos3 = 0
					res3 = args[pos3:(pos3 + 1)]
					del args[pos3:(pos3 + 1)]
					res3
					break
				elif (tag == "--all"):
					more = True
					self.flags.show_unchanged = True
					self.flags.show_unchanged_columns = True
					pos4 = i
					if (pos4 < 0):
						pos4 = (python_lib_Builtin.len(args) + pos4)
					if (pos4 < 0):
						pos4 = 0
					res4 = args[pos4:(pos4 + 1)]
					del args[pos4:(pos4 + 1)]
					res4
					break
				elif (tag == "--all-rows"):
					more = True
					self.flags.show_unchanged = True
					pos5 = i
					if (pos5 < 0):
						pos5 = (python_lib_Builtin.len(args) + pos5)
					if (pos5 < 0):
						pos5 = 0
					res5 = args[pos5:(pos5 + 1)]
					del args[pos5:(pos5 + 1)]
					res5
					break
				elif (tag == "--all-columns"):
					more = True
					self.flags.show_unchanged_columns = True
					pos6 = i
					if (pos6 < 0):
						pos6 = (python_lib_Builtin.len(args) + pos6)
					if (pos6 < 0):
						pos6 = 0
					res6 = args[pos6:(pos6 + 1)]
					del args[pos6:(pos6 + 1)]
					res6
					break
				elif (tag == "--act"):
					more = True
					if (self.flags.acts is None):
						self.flags.acts = haxe_ds_StringMap()
					self.flags.acts.h[python_internal_ArrayImpl._get(args, (i + 1))] = True
					True
					pos7 = i
					if (pos7 < 0):
						pos7 = (python_lib_Builtin.len(args) + pos7)
					if (pos7 < 0):
						pos7 = 0
					res7 = args[pos7:(pos7 + 2)]
					del args[pos7:(pos7 + 2)]
					res7
					break
				elif (tag == "--context"):
					more = True
					context = Std.parseInt(python_internal_ArrayImpl._get(args, (i + 1)))
					if (context >= 0):
						self.flags.unchanged_context = context
					pos8 = i
					if (pos8 < 0):
						pos8 = (python_lib_Builtin.len(args) + pos8)
					if (pos8 < 0):
						pos8 = 0
					res8 = args[pos8:(pos8 + 2)]
					del args[pos8:(pos8 + 2)]
					res8
					break
				elif (tag == "--inplace"):
					more = True
					inplace = True
					pos9 = i
					if (pos9 < 0):
						pos9 = (python_lib_Builtin.len(args) + pos9)
					if (pos9 < 0):
						pos9 = 0
					res9 = args[pos9:(pos9 + 1)]
					del args[pos9:(pos9 + 1)]
					res9
					break
				elif (tag == "--git"):
					more = True
					git = True
					pos10 = i
					if (pos10 < 0):
						pos10 = (python_lib_Builtin.len(args) + pos10)
					if (pos10 < 0):
						pos10 = 0
					res10 = args[pos10:(pos10 + 1)]
					del args[pos10:(pos10 + 1)]
					res10
					break
				elif (tag == "--unordered"):
					more = True
					self.flags.ordered = False
					self.flags.unchanged_context = 0
					self.order_set = True
					pos11 = i
					if (pos11 < 0):
						pos11 = (python_lib_Builtin.len(args) + pos11)
					if (pos11 < 0):
						pos11 = 0
					res11 = args[pos11:(pos11 + 1)]
					del args[pos11:(pos11 + 1)]
					res11
					break
				elif (tag == "--ordered"):
					more = True
					self.flags.ordered = True
					self.order_set = True
					pos12 = i
					if (pos12 < 0):
						pos12 = (python_lib_Builtin.len(args) + pos12)
					if (pos12 < 0):
						pos12 = 0
					res12 = args[pos12:(pos12 + 1)]
					del args[pos12:(pos12 + 1)]
					res12
					break
				elif (tag == "--color"):
					more = True
					self.flags.terminal_format = "ansi"
					pos13 = i
					if (pos13 < 0):
						pos13 = (python_lib_Builtin.len(args) + pos13)
					if (pos13 < 0):
						pos13 = 0
					res13 = args[pos13:(pos13 + 1)]
					del args[pos13:(pos13 + 1)]
					res13
					break
				elif (tag == "--no-color"):
					more = True
					self.flags.terminal_format = "plain"
					pos14 = i
					if (pos14 < 0):
						pos14 = (python_lib_Builtin.len(args) + pos14)
					if (pos14 < 0):
						pos14 = 0
					res14 = args[pos14:(pos14 + 1)]
					del args[pos14:(pos14 + 1)]
					res14
					break
				elif (tag == "--input-format"):
					more = True
					self.setFormat(python_internal_ArrayImpl._get(args, (i + 1)))
					pos15 = i
					if (pos15 < 0):
						pos15 = (python_lib_Builtin.len(args) + pos15)
					if (pos15 < 0):
						pos15 = 0
					res15 = args[pos15:(pos15 + 2)]
					del args[pos15:(pos15 + 2)]
					res15
					break
				elif (tag == "--output-format"):
					more = True
					self.output_format = python_internal_ArrayImpl._get(args, (i + 1))
					self.output_format_set = True
					pos16 = i
					if (pos16 < 0):
						pos16 = (python_lib_Builtin.len(args) + pos16)
					if (pos16 < 0):
						pos16 = 0
					res16 = args[pos16:(pos16 + 2)]
					del args[pos16:(pos16 + 2)]
					res16
					break
				elif (tag == "--id"):
					more = True
					if (self.flags.ids is None):
						self.flags.ids = list()
					_this = self.flags.ids
					_this.append(python_internal_ArrayImpl._get(args, (i + 1)))
					python_lib_Builtin.len(_this)
					pos17 = i
					if (pos17 < 0):
						pos17 = (python_lib_Builtin.len(args) + pos17)
					if (pos17 < 0):
						pos17 = 0
					res17 = args[pos17:(pos17 + 2)]
					del args[pos17:(pos17 + 2)]
					res17
					break
				elif (tag == "--ignore"):
					more = True
					self.flags.ignoreColumn(python_internal_ArrayImpl._get(args, (i + 1)))
					pos18 = i
					if (pos18 < 0):
						pos18 = (python_lib_Builtin.len(args) + pos18)
					if (pos18 < 0):
						pos18 = 0
					res18 = args[pos18:(pos18 + 2)]
					del args[pos18:(pos18 + 2)]
					res18
					break
				elif (tag == "--index"):
					more = True
					self.flags.always_show_order = True
					self.flags.never_show_order = False
					pos19 = i
					if (pos19 < 0):
						pos19 = (python_lib_Builtin.len(args) + pos19)
					if (pos19 < 0):
						pos19 = 0
					res19 = args[pos19:(pos19 + 1)]
					del args[pos19:(pos19 + 1)]
					res19
					break
				elif (tag == "--www"):
					more = True
					self.output_format = "www"
					self.output_format_set = True
					pos20 = i
					if (pos20 < 0):
						pos20 = (python_lib_Builtin.len(args) + pos20)
					if (pos20 < 0):
						pos20 = 0
					res20 = args[pos20:(pos20 + 1)]
					del args[pos20:(pos20 + 1)]
					res20
				elif (tag == "--table"):
					more = True
					self.flags.addTable(python_internal_ArrayImpl._get(args, (i + 1)))
					pos21 = i
					if (pos21 < 0):
						pos21 = (python_lib_Builtin.len(args) + pos21)
					if (pos21 < 0):
						pos21 = 0
					res21 = args[pos21:(pos21 + 2)]
					del args[pos21:(pos21 + 2)]
					res21
					break
				elif ((tag == "-w") or ((tag == "--ignore-whitespace"))):
					more = True
					self.flags.ignore_whitespace = True
					pos22 = i
					if (pos22 < 0):
						pos22 = (python_lib_Builtin.len(args) + pos22)
					if (pos22 < 0):
						pos22 = 0
					res22 = args[pos22:(pos22 + 1)]
					del args[pos22:(pos22 + 1)]
					res22
					break
				elif ((tag == "-i") or ((tag == "--ignore-case"))):
					more = True
					self.flags.ignore_case = True
					pos23 = i
					if (pos23 < 0):
						pos23 = (python_lib_Builtin.len(args) + pos23)
					if (pos23 < 0):
						pos23 = 0
					res23 = args[pos23:(pos23 + 1)]
					del args[pos23:(pos23 + 1)]
					res23
					break
				elif (tag == "--padding"):
					more = True
					self.flags.padding_strategy = python_internal_ArrayImpl._get(args, (i + 1))
					pos24 = i
					if (pos24 < 0):
						pos24 = (python_lib_Builtin.len(args) + pos24)
					if (pos24 < 0):
						pos24 = 0
					res24 = args[pos24:(pos24 + 2)]
					del args[pos24:(pos24 + 2)]
					res24
					break
		cmd = (args[0] if 0 < python_lib_Builtin.len(args) else None)
		if (python_lib_Builtin.len(args) < 2):
			if (cmd == "version"):
				io.writeStdout((HxOverrides.stringOrNull(Coopy.VERSION) + "\n"))
				return 0
			if (cmd == "git"):
				io.writeStdout("You can use daff to improve git's handling of csv files, by using it as a\ndiff driver (for showing what has changed) and as a merge driver (for merging\nchanges between multiple versions).\n")
				io.writeStdout("\n")
				io.writeStdout("Automatic setup\n")
				io.writeStdout("---------------\n\n")
				io.writeStdout("Run:\n")
				io.writeStdout("  daff git csv\n")
				io.writeStdout("\n")
				io.writeStdout("Manual setup\n")
				io.writeStdout("------------\n\n")
				io.writeStdout("Create and add a file called .gitattributes in the root directory of your\nrepository, containing:\n\n")
				io.writeStdout("  *.csv diff=daff-csv\n")
				io.writeStdout("  *.csv merge=daff-csv\n")
				io.writeStdout("\nCreate a file called .gitconfig in your home directory (or alternatively\nopen .git/config for a particular repository) and add:\n\n")
				io.writeStdout("  [diff \"daff-csv\"]\n")
				io.writeStdout("  command = daff diff --git\n")
				io.writeStderr("\n")
				io.writeStdout("  [merge \"daff-csv\"]\n")
				io.writeStdout("  name = daff tabular merge\n")
				io.writeStdout("  driver = daff merge --output %A %O %A %B\n\n")
				io.writeStderr("Make sure you can run daff from the command-line as just \"daff\" - if not,\nreplace \"daff\" in the driver and command lines above with the correct way\nto call it. Add --no-color if your terminal does not support ANSI colors.")
				io.writeStderr("\n")
				return 0
			io.writeStderr("daff can produce and apply tabular diffs.\n")
			io.writeStderr("Call as:\n")
			io.writeStderr("  daff [--color] [--no-color] [--output OUTPUT.csv] a.csv b.csv\n")
			io.writeStderr("  daff [--output OUTPUT.html] a.csv b.csv\n")
			io.writeStderr("  daff [--output OUTPUT.csv] parent.csv a.csv b.csv\n")
			io.writeStderr("  daff [--output OUTPUT.ndjson] a.ndjson b.ndjson\n")
			io.writeStderr("  daff [--www] a.csv b.csv\n")
			io.writeStderr("  daff patch [--inplace] [--output OUTPUT.csv] a.csv patch.csv\n")
			io.writeStderr("  daff merge [--inplace] [--output OUTPUT.csv] parent.csv a.csv b.csv\n")
			io.writeStderr("  daff trim [--output OUTPUT.csv] source.csv\n")
			io.writeStderr("  daff render [--output OUTPUT.html] diff.csv\n")
			io.writeStderr("  daff copy in.csv out.tsv\n")
			io.writeStderr("  daff git\n")
			io.writeStderr("  daff version\n")
			io.writeStderr("\n")
			io.writeStderr("The --inplace option to patch and merge will result in modification of a.csv.\n")
			io.writeStderr("\n")
			io.writeStderr("If you need more control, here is the full list of flags:\n")
			io.writeStderr("  daff diff [--output OUTPUT.csv] [--context NUM] [--all] [--act ACT] a.csv b.csv\n")
			io.writeStderr("     --act ACT:     show only a certain kind of change (update, insert, delete)\n")
			io.writeStderr("     --all:         do not prune unchanged rows or columns\n")
			io.writeStderr("     --all-rows:    do not prune unchanged rows\n")
			io.writeStderr("     --all-columns: do not prune unchanged columns\n")
			io.writeStderr("     --color:       highlight changes with terminal colors (default in terminals)\n")
			io.writeStderr("     --context NUM: show NUM rows of context\n")
			io.writeStderr("     --id:          specify column to use as primary key (repeat for multi-column key)\n")
			io.writeStderr("     --ignore:      specify column to ignore completely (can repeat)\n")
			io.writeStderr("     --index:       include row/columns numbers from original tables\n")
			io.writeStderr("     --input-format [csv|tsv|ssv|json]: set format to expect for input\n")
			io.writeStderr("     --no-color:    make sure terminal colors are not used\n")
			io.writeStderr("     --ordered:     assume row order is meaningful (default for CSV)\n")
			io.writeStderr("     --output-format [csv|tsv|ssv|json|copy|html]: set format for output\n")
			io.writeStderr("     --padding [dense|sparse|smart]: set padding method for aligning columns\n")
			io.writeStderr("     --table NAME:  compare the named table, used with SQL sources\n")
			io.writeStderr("     --unordered:   assume row order is meaningless (default for json formats)\n")
			io.writeStderr("     -w / --ignore-whitespace: ignore changes in leading/trailing whitespace\n")
			io.writeStderr("     -i / --ignore-case: ignore differences in case\n")
			io.writeStderr("\n")
			io.writeStderr("  daff render [--output OUTPUT.html] [--css CSS.css] [--fragment] [--plain] diff.csv\n")
			io.writeStderr("     --css CSS.css: generate a suitable css file to go with the html\n")
			io.writeStderr("     --fragment:    generate just a html fragment rather than a page\n")
			io.writeStderr("     --plain:       do not use fancy utf8 characters to make arrows prettier\n")
			io.writeStderr("     --www:         send output to a browser\n")
			return 1
		cmd1 = (args[0] if 0 < python_lib_Builtin.len(args) else None)
		offset = 1
		if (not Lambda.has(["diff", "patch", "merge", "trim", "render", "git", "version", "copy"],cmd1)):
			if ((cmd1.find(".") != -1) or ((cmd1.find("--") == 0))):
				cmd1 = "diff"
				offset = 0
		if (cmd1 == "git"):
			types = None
			len = (python_lib_Builtin.len(args) - offset)
			pos25 = offset
			if (pos25 < 0):
				pos25 = (python_lib_Builtin.len(args) + pos25)
			if (pos25 < 0):
				pos25 = 0
			res25 = args[pos25:(pos25 + len)]
			del args[pos25:(pos25 + len)]
			types = res25
			return self.installGitDriver(io,types)
		if git:
			ct = (python_lib_Builtin.len(args) - offset)
			if ((ct != 7) and ((ct != 9))):
				io.writeStderr((("Expected 7 or 9 parameters from git, but got " + Std.string(ct)) + "\n"))
				return 1
			git_args = None
			pos26 = offset
			if (pos26 < 0):
				pos26 = (python_lib_Builtin.len(args) + pos26)
			if (pos26 < 0):
				pos26 = 0
			res26 = args[pos26:(pos26 + ct)]
			del args[pos26:(pos26 + ct)]
			git_args = res26
			len1 = python_lib_Builtin.len(args)
			pos27 = 0
			if (pos27 < 0):
				pos27 = (python_lib_Builtin.len(args) + pos27)
			if (pos27 < 0):
				pos27 = 0
			res27 = args[pos27:(pos27 + len1)]
			del args[pos27:(pos27 + len1)]
			res27
			offset = 0
			old_display_path = (git_args[0] if 0 < python_lib_Builtin.len(git_args) else None)
			new_display_path = (git_args[0] if 0 < python_lib_Builtin.len(git_args) else None)
			old_file = (git_args[1] if 1 < python_lib_Builtin.len(git_args) else None)
			new_file = (git_args[4] if 4 < python_lib_Builtin.len(git_args) else None)
			if (ct == 9):
				io.writeStdout((git_args[8] if 8 < python_lib_Builtin.len(git_args) else None))
				new_display_path = (git_args[7] if 7 < python_lib_Builtin.len(git_args) else None)
			io.writeStdout((("--- a/" + HxOverrides.stringOrNull(old_display_path)) + "\n"))
			io.writeStdout((("+++ b/" + HxOverrides.stringOrNull(new_display_path)) + "\n"))
			args.append(old_file)
			python_lib_Builtin.len(args)
			args.append(new_file)
			python_lib_Builtin.len(args)
		parent = None
		if ((python_lib_Builtin.len(args) - offset) >= 3):
			parent = self.loadTable((args[offset] if offset >= 0 and offset < python_lib_Builtin.len(args) else None))
			offset = (offset + 1)
		aname = (args[offset] if offset >= 0 and offset < python_lib_Builtin.len(args) else None)
		a = self.loadTable(aname)
		b = None
		if ((python_lib_Builtin.len(args) - offset) >= 2):
			if (cmd1 != "copy"):
				b = self.loadTable(python_internal_ArrayImpl._get(args, (1 + offset)))
			else:
				output = python_internal_ArrayImpl._get(args, (1 + offset))
		self.flags.diff_strategy = self.strategy
		if inplace:
			if (output is not None):
				io.writeStderr("Please do not use --inplace when specifying an output.\n")
			output = aname
			return 1
		if (output is None):
			output = "-"
		ok = True
		if (cmd1 == "diff"):
			if (not self.order_set):
				self.flags.ordered = self.order_preference
				if (not self.flags.ordered):
					self.flags.unchanged_context = 0
			self.flags.allow_nested_cells = self.nested_output
			self.runDiff(parent,a,b,self.flags,output)
		elif (cmd1 == "patch"):
			patcher = HighlightPatch(a, b)
			patcher.apply()
			self.saveTable(output,a)
		elif (cmd1 == "merge"):
			merger = Merger(parent, a, b, self.flags)
			conflicts = merger.apply()
			ok = (conflicts == 0)
			if (conflicts > 0):
				io.writeStderr((((Std.string(conflicts) + " conflict") + HxOverrides.stringOrNull((("s" if ((conflicts > 1)) else "")))) + "\n"))
			self.saveTable(output,a)
		elif (cmd1 == "trim"):
			self.saveTable(output,a)
		elif (cmd1 == "render"):
			self.renderTable(output,a)
		elif (cmd1 == "copy"):
			self.saveTable(output,a)
		if ok:
			return 0
		else:
			return 1

	def coopyhx(self,io):
		args = io.args()
		if ((args[0] if 0 < python_lib_Builtin.len(args) else None) == "--keep"):
			return Coopy.keepAround()
		return self.run(args,io)

	@staticmethod
	def diffAsHtml(local,remote,flags = None):
		comp = TableComparisonState()
		td = Coopy.align(local,remote,flags,comp)
		o = Coopy.getBlankTable(td,comp)
		if (comp.a is not None):
			o = comp.a.create()
		if ((o is None) and ((comp.b is not None))):
			o = comp.b.create()
		if (o is None):
			o = SimpleTable(0, 0)
		os = Tables(o)
		td.hiliteWithNesting(os)
		render = DiffRender()
		return render.renderTables(os).html()

	@staticmethod
	def diffAsAnsi(local,remote,flags = None):
		tool = Coopy(TableIO())
		tool.cache_txt = ""
		if (flags is None):
			flags = CompareFlags()
		tool.output_format = "csv"
		tool.runDiff(flags.parent,local,remote,flags,None)
		return tool.cache_txt

	@staticmethod
	def diff(local,remote,flags = None):
		comp = TableComparisonState()
		td = Coopy.align(local,remote,flags,comp)
		o = Coopy.getBlankTable(td,comp)
		if (comp.a is not None):
			o = comp.a.create()
		if ((o is None) and ((comp.b is not None))):
			o = comp.b.create()
		if (o is None):
			o = SimpleTable(0, 0)
		td.hilite(o)
		return o

	@staticmethod
	def getBlankTable(td,comp):
		o = None
		if (comp.a is not None):
			o = comp.a.create()
		if ((o is None) and ((comp.b is not None))):
			o = comp.b.create()
		if (o is None):
			o = SimpleTable(0, 0)
		return o

	@staticmethod
	def align(local,remote,flags,comp):
		comp.a = Coopy.tablify(local)
		comp.b = Coopy.tablify(remote)
		if (flags is None):
			flags = CompareFlags()
		comp.compare_flags = flags
		ct = CompareTable(comp)
		align = ct.align()
		td = TableDiff(align, flags)
		return td

	@staticmethod
	def patch(local,patch,flags = None):
		patcher = HighlightPatch(Coopy.tablify(local), Coopy.tablify(patch))
		return patcher.apply()

	@staticmethod
	def compareTables(local,remote,flags = None):
		comp = TableComparisonState()
		comp.a = Coopy.tablify(local)
		comp.b = Coopy.tablify(remote)
		comp.compare_flags = flags
		ct = CompareTable(comp)
		return ct

	@staticmethod
	def compareTables3(parent,local,remote,flags = None):
		comp = TableComparisonState()
		comp.p = Coopy.tablify(parent)
		comp.a = Coopy.tablify(local)
		comp.b = Coopy.tablify(remote)
		comp.compare_flags = flags
		ct = CompareTable(comp)
		return ct

	@staticmethod
	def keepAround():
		st = SimpleTable(1, 1)
		v = Viterbi()
		td = TableDiff(None, None)
		cf = CompareFlags()
		idx = Index(cf)
		dr = DiffRender()
		hp = HighlightPatch(None, None)
		csv = Csv()
		tm = TableModifier(None)
		sc = SqlCompare(None, None, None, None)
		sq = SqliteHelper()
		sm = SimpleMeta(None)
		ct = CombinedTable(None)
		return 0

	@staticmethod
	def cellFor(x):
		return x

	@staticmethod
	def main():
		io = TableIO()
		coopy = Coopy()
		return coopy.coopyhx(io)

	@staticmethod
	def show(t):
		w = t.get_width()
		h = t.get_height()
		txt = ""
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				txt = (HxOverrides.stringOrNull(txt) + Std.string(t.getCell(x,y)))
				txt = (HxOverrides.stringOrNull(txt) + " ")
			txt = (HxOverrides.stringOrNull(txt) + "\n")
		haxe_Log.trace(txt,_hx_AnonObject({'fileName': "Coopy.hx", 'lineNumber': 1071, 'className': "Coopy", 'methodName': "show"}))

	@staticmethod
	def jsonify(t):
		workbook = haxe_ds_StringMap()
		sheet = list()
		w = t.get_width()
		h = t.get_height()
		txt = ""
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			row = list()
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				v = t.getCell(x,y)
				row.append(v)
				python_lib_Builtin.len(row)
			sheet.append(row)
			python_lib_Builtin.len(sheet)
		workbook.h["sheet"] = sheet
		return workbook

	@staticmethod
	def tablify(data):
		if (data is None):
			return data
		get_cell_view = python_Boot.field(data,"getCellView")
		if (get_cell_view is not None):
			return data
		daff = __import__('daff')
		return daff.PythonTableView(data)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.format_preference = None
		_hx_o.delim_preference = None
		_hx_o.extern_preference = None
		_hx_o.output_format = None
		_hx_o.output_format_set = None
		_hx_o.nested_output = None
		_hx_o.order_set = None
		_hx_o.order_preference = None
		_hx_o.io = None
		_hx_o.pretty = None
		_hx_o.strategy = None
		_hx_o.css_output = None
		_hx_o.fragment = None
		_hx_o.flags = None
		_hx_o.cache_txt = None
		_hx_o.mv = None
		_hx_o.status = None
		_hx_o.daff_cmd = None


Coopy = _hx_classes.registerClass("Coopy", fields=["format_preference","delim_preference","extern_preference","output_format","output_format_set","nested_output","order_set","order_preference","io","pretty","strategy","css_output","fragment","flags","cache_txt","mv","status","daff_cmd"], methods=["init","checkFormat","setFormat","getRenderer","applyRenderer","renderTable","renderTables","saveTable","encodeTable","saveTables","saveText","jsonToTables","jsonToTable","runDiff","loadTable","command","installGitDriver","run","coopyhx"], statics=["VERSION","diffAsHtml","diffAsAnsi","diff","getBlankTable","align","patch","compareTables","compareTables3","keepAround","cellFor","main","show","jsonify","tablify"])(Coopy)

class CrossMatch(object):

	def __init__(self):
		self.spot_a = None
		self.spot_b = None
		self.item_a = None
		self.item_b = None
		pass

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.spot_a = None
		_hx_o.spot_b = None
		_hx_o.item_a = None
		_hx_o.item_b = None


CrossMatch = _hx_classes.registerClass("CrossMatch", fields=["spot_a","spot_b","item_a","item_b"])(CrossMatch)

class Csv(object):

	def __init__(self,delim = ","):
		if (delim is None):
			delim = ","
		self.cursor = None
		self.row_ended = None
		self.has_structure = None
		self.delim = None
		self.cursor = 0
		self.row_ended = False
		if (delim is None):
			self.delim = ","
		else:
			self.delim = delim

	def renderTable(self,t):
		result = ""
		txt = ""
		v = t.getCellView()
		stream = TableStream(t)
		w = stream.width()
		while (stream.fetch()):
			_g = 0
			while ((_g < w)):
				x = _g
				_g = (_g + 1)
				if (x > 0):
					txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.delim))
				txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.renderCell(v,stream.getCell(x))))
			txt = (HxOverrides.stringOrNull(txt) + "\r\n")
		return txt

	def renderCell(self,v,d):
		if (d is None):
			return "NULL"
		unicode = v.toString(d)
		need_quote = False
		_g1 = 0
		_g = python_lib_Builtin.len(unicode)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ch = None
			if ((i < 0) or ((i >= python_lib_Builtin.len(unicode)))):
				ch = ""
			else:
				ch = unicode[i]
			if (((((((ch == "\"") or ((ch == "'"))) or ((ch == self.delim))) or ((ch == "\r"))) or ((ch == "\n"))) or ((ch == "\t"))) or ((ch == " "))):
				need_quote = True
				break
		result = ""
		if need_quote:
			result = (HxOverrides.stringOrNull(result) + "\"")
		line_buf = ""
		_g11 = 0
		_g2 = python_lib_Builtin.len(unicode)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			ch1 = None
			if ((i1 < 0) or ((i1 >= python_lib_Builtin.len(unicode)))):
				ch1 = ""
			else:
				ch1 = unicode[i1]
			if (ch1 == "\""):
				result = (HxOverrides.stringOrNull(result) + "\"")
			if ((ch1 != "\r") and ((ch1 != "\n"))):
				if (python_lib_Builtin.len(line_buf) > 0):
					result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull(line_buf))
					line_buf = ""
				result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull(ch1))
			else:
				line_buf = (HxOverrides.stringOrNull(line_buf) + HxOverrides.stringOrNull(ch1))
		if need_quote:
			result = (HxOverrides.stringOrNull(result) + "\"")
		return result

	def parseTable(self,txt,tab):
		if (not tab.isResizable()):
			return False
		self.cursor = 0
		self.row_ended = False
		self.has_structure = True
		tab.resize(0,0)
		w = 0
		h = 0
		at = 0
		yat = 0
		while ((self.cursor < python_lib_Builtin.len(txt))):
			cell = self.parseCellPart(txt)
			if (yat >= h):
				h = (yat + 1)
				tab.resize(w,h)
			if (at >= w):
				if (yat > 0):
					if ((cell != "") and ((cell is not None))):
						context = ""
						_g = 0
						while ((_g < w)):
							i = _g
							_g = (_g + 1)
							if (i > 0):
								context = (HxOverrides.stringOrNull(context) + ",")
							context = (HxOverrides.stringOrNull(context) + Std.string(tab.getCell(i,yat)))
						haxe_Log.trace(((((("Ignored overflowing row " + Std.string(yat)) + " with cell '") + HxOverrides.stringOrNull(cell)) + "' after: ") + HxOverrides.stringOrNull(context)),_hx_AnonObject({'fileName': "Csv.hx", 'lineNumber': 137, 'className': "Csv", 'methodName': "parseTable"}))
				else:
					w = (at + 1)
					tab.resize(w,h)
			tab.setCell(at,(h - 1),cell)
			at = (at + 1)
			if self.row_ended:
				at = 0
				yat = (yat + 1)
			_hx_local_4 = self
			_hx_local_5 = _hx_local_4.cursor
			_hx_local_4.cursor = (_hx_local_5 + 1)
			_hx_local_5
		return True

	def makeTable(self,txt):
		tab = SimpleTable(0, 0)
		self.parseTable(txt,tab)
		return tab

	def parseCellPart(self,txt):
		if (txt is None):
			return None
		self.row_ended = False
		first_non_underscore = python_lib_Builtin.len(txt)
		last_processed = 0
		quoting = False
		quote = 0
		result = ""
		start = self.cursor
		_g1 = self.cursor
		_g = python_lib_Builtin.len(txt)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ch = HxString.charCodeAt(txt,i)
			last_processed = i
			if ((ch != 95) and ((i < first_non_underscore))):
				first_non_underscore = i
			if self.has_structure:
				if (not quoting):
					if (ch == HxString.charCodeAt(self.delim,0)):
						break
					if ((ch == 13) or ((ch == 10))):
						ch2 = HxString.charCodeAt(txt,(i + 1))
						if (ch2 is not None):
							if (ch2 != ch):
								if ((ch2 == 13) or ((ch2 == 10))):
									last_processed = (last_processed + 1)
						self.row_ended = True
						break
					if (ch == 34):
						if (i == self.cursor):
							quoting = True
							quote = ch
							if (i != start):
								result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull("".join(python_lib_Builtin.map(hxunichr,[ch]))))
							continue
						elif (ch == quote):
							quoting = True
					result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull("".join(python_lib_Builtin.map(hxunichr,[ch]))))
					continue
				if (ch == quote):
					quoting = False
					continue
			result = (HxOverrides.stringOrNull(result) + HxOverrides.stringOrNull("".join(python_lib_Builtin.map(hxunichr,[ch]))))
		self.cursor = last_processed
		if (quote == 0):
			if (result == "NULL"):
				return None
			if (first_non_underscore > start):
				_hx_del = (first_non_underscore - start)
				if (HxString.substr(result,_hx_del,None) == "NULL"):
					return HxString.substr(result,1,None)
		return result

	def parseCell(self,txt):
		self.cursor = 0
		self.row_ended = False
		self.has_structure = False
		return self.parseCellPart(txt)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.cursor = None
		_hx_o.row_ended = None
		_hx_o.has_structure = None
		_hx_o.delim = None


Csv = _hx_classes.registerClass("Csv", fields=["cursor","row_ended","has_structure","delim"], methods=["renderTable","renderCell","parseTable","makeTable","parseCellPart","parseCell"])(Csv)

class Date(object):

	def toString(self):
		m = ((self.date.month - 1) + 1)
		d = self.date.day
		h = self.date.hour
		mi = self.date.minute
		s = self.date.second
		return ((((((((((Std.string(self.date.year) + "-") + HxOverrides.stringOrNull(((("0" + Std.string(m)) if ((m < 10)) else ("" + Std.string(m)))))) + "-") + HxOverrides.stringOrNull(((("0" + Std.string(d)) if ((d < 10)) else ("" + Std.string(d)))))) + " ") + HxOverrides.stringOrNull(((("0" + Std.string(h)) if ((h < 10)) else ("" + Std.string(h)))))) + ":") + HxOverrides.stringOrNull(((("0" + Std.string(mi)) if ((mi < 10)) else ("" + Std.string(mi)))))) + ":") + HxOverrides.stringOrNull(((("0" + Std.string(s)) if ((s < 10)) else ("" + Std.string(s))))))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.date = None


Date = _hx_classes.registerClass("Date", fields=["date"], methods=["toString"])(Date)

class DiffRender(object):

	def __init__(self):
		self.text_to_insert = None
		self.td_open = None
		self.td_close = None
		self.open = None
		self.pretty_arrows = None
		self.section = None
		self.text_to_insert = list()
		self.open = False
		self.pretty_arrows = True

	def usePrettyArrows(self,flag):
		self.pretty_arrows = flag

	def insert(self,unicode):
		_this = self.text_to_insert
		_this.append(unicode)
		python_lib_Builtin.len(_this)

	def beginTable(self):
		self.insert("<table>\n")
		self.section = None

	def setSection(self,unicode):
		if (unicode == self.section):
			return
		if (self.section is not None):
			self.insert("</t")
			self.insert(self.section)
			self.insert(">\n")
		self.section = unicode
		if (self.section is not None):
			self.insert("<t")
			self.insert(self.section)
			self.insert(">\n")

	def beginRow(self,mode):
		self.td_open = "<td"
		self.td_close = "</td>"
		row_class = ""
		if (mode == "header"):
			self.td_open = "<th"
			self.td_close = "</th>"
		row_class = mode
		tr = "<tr>"
		if (row_class != ""):
			tr = (("<tr class=\"" + HxOverrides.stringOrNull(row_class)) + "\">")
		self.insert(tr)

	def insertCell(self,txt,mode):
		cell_decorate = ""
		if (mode != ""):
			cell_decorate = ((" class=\"" + HxOverrides.stringOrNull(mode)) + "\"")
		self.insert(((HxOverrides.stringOrNull(self.td_open) + HxOverrides.stringOrNull(cell_decorate)) + ">"))
		if (txt is not None):
			self.insert(txt)
		else:
			self.insert("null")
		self.insert(self.td_close)

	def endRow(self):
		self.insert("</tr>\n")

	def endTable(self):
		self.setSection(None)
		self.insert("</table>\n")

	def html(self):
		return "".join([python_Boot.toString1(x1,'') for x1 in self.text_to_insert])

	def toString(self):
		return self.html()

	def render(self,tab):
		tab = Coopy.tablify(tab)
		if ((tab.get_width() == 0) or ((tab.get_height() == 0))):
			return self
		render = self
		render.beginTable()
		change_row = -1
		cell = CellInfo()
		view = tab.getCellView()
		corner = view.toString(tab.getCell(0,0))
		off = None
		if (corner == "@:@"):
			off = 1
		else:
			off = 0
		if (off > 0):
			if ((tab.get_width() <= 1) or ((tab.get_height() <= 1))):
				return self
		_g1 = 0
		_g = tab.get_height()
		while ((_g1 < _g)):
			row = _g1
			_g1 = (_g1 + 1)
			open = False
			txt = view.toString(tab.getCell(off,row))
			if (txt is None):
				txt = ""
			DiffRender.examineCell(off,row,view,txt,"",txt,corner,cell,off)
			row_mode = cell.category
			if (row_mode == "spec"):
				change_row = row
			if ((((row_mode == "header") or ((row_mode == "spec"))) or ((row_mode == "index"))) or ((row_mode == "meta"))):
				self.setSection("head")
			else:
				self.setSection("body")
			render.beginRow(row_mode)
			_g3 = 0
			_g2 = tab.get_width()
			while ((_g3 < _g2)):
				c = _g3
				_g3 = (_g3 + 1)
				DiffRender.examineCell(c,row,view,tab.getCell(c,row),(view.toString(tab.getCell(c,change_row)) if ((change_row >= 0)) else ""),txt,corner,cell,off)
				render.insertCell((cell.pretty_value if (self.pretty_arrows) else cell.value),cell.category_given_tr)
			render.endRow()
		render.endTable()
		return self

	def renderTables(self,tabs):
		order = tabs.getOrder()
		if ((python_lib_Builtin.len(order) == 0) or tabs.hasInsDel()):
			self.render(tabs.one())
		_g1 = 1
		_g = python_lib_Builtin.len(order)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			name = (order[i] if i >= 0 and i < python_lib_Builtin.len(order) else None)
			tab = tabs.get(name)
			if (tab.get_height() <= 1):
				continue
			self.insert("<h3>")
			self.insert(name)
			self.insert("</h3>\n")
			self.render(tab)
		return self

	def sampleCss(self):
		return ".highlighter .add { \n  background-color: #7fff7f;\n}\n\n.highlighter .remove { \n  background-color: #ff7f7f;\n}\n\n.highlighter td.modify { \n  background-color: #7f7fff;\n}\n\n.highlighter td.conflict { \n  background-color: #f00;\n}\n\n.highlighter .spec { \n  background-color: #aaa;\n}\n\n.highlighter .move { \n  background-color: #ffa;\n}\n\n.highlighter .null { \n  color: #888;\n}\n\n.highlighter table { \n  border-collapse:collapse;\n}\n\n.highlighter td, .highlighter th {\n  border: 1px solid #2D4068;\n  padding: 3px 7px 2px;\n}\n\n.highlighter th, .highlighter .header, .highlighter .meta {\n  background-color: #aaf;\n  font-weight: bold;\n  padding-bottom: 4px;\n  padding-top: 5px;\n  text-align:left;\n}\n\n.highlighter tr.header th {\n  border-bottom: 2px solid black;\n}\n\n.highlighter tr.index td, .highlighter .index, .highlighter tr.header th.index {\n  background-color: white;\n  border: none;\n}\n\n.highlighter .gap {\n  color: #888;\n}\n\n.highlighter td {\n  empty-cells: show;\n}\n"

	def completeHtml(self):
		self.text_to_insert.insert(0, "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='utf-8'>\n<style TYPE='text/css'>\n")
		x = self.sampleCss()
		self.text_to_insert.insert(1, x)
		self.text_to_insert.insert(2, "</style>\n</head>\n<body>\n<div class='highlighter'>\n")
		_this = self.text_to_insert
		_this.append("</div>\n</body>\n</html>\n")
		python_lib_Builtin.len(_this)

	@staticmethod
	def examineCell(x,y,view,raw,vcol,vrow,vcorner,cell,offset = 0):
		if (offset is None):
			offset = 0
		nested = view.isHash(raw)
		cell.category = ""
		cell.category_given_tr = ""
		cell.separator = ""
		cell.pretty_separator = ""
		cell.conflicted = False
		cell.updated = False
		def _hx_local_2():
			def _hx_local_1():
				def _hx_local_0():
					cell.rvalue = None
					return cell.rvalue
				cell.lvalue = _hx_local_0()
				return cell.lvalue
			cell.pvalue = _hx_local_1()
			return cell.pvalue
		cell.meta = _hx_local_2()
		cell.value = raw
		cell.pretty_value = cell.value
		if (vrow is None):
			vrow = ""
		if (vcol is None):
			vcol = ""
		if (((python_lib_Builtin.len(vrow) >= 3) and (((("" if ((0 >= python_lib_Builtin.len(vrow))) else vrow[0])) == "@"))) and (((("" if ((1 >= python_lib_Builtin.len(vrow))) else vrow[1])) != "@"))):
			idx = vrow.find("@", 1)
			if (idx >= 0):
				cell.meta = HxString.substr(vrow,1,(idx - 1))
				vrow = HxString.substr(vrow,(idx + 1),python_lib_Builtin.len(vrow))
				cell.category = "meta"
		removed_column = False
		if (vrow == ":"):
			cell.category = "move"
		if (((vrow == "") and ((offset == 1))) and ((y == 0))):
			cell.category = "index"
		if (vcol.find("+++") >= 0):
			def _hx_local_3():
				cell.category = "add"
				return cell.category
			cell.category_given_tr = _hx_local_3()
		elif (vcol.find("---") >= 0):
			def _hx_local_4():
				cell.category = "remove"
				return cell.category
			cell.category_given_tr = _hx_local_4()
			removed_column = True
		if (vrow == "!"):
			cell.category = "spec"
		elif (vrow == "@@"):
			cell.category = "header"
		elif (vrow == "..."):
			cell.category = "gap"
		elif (vrow == "+++"):
			if (not removed_column):
				cell.category = "add"
		elif (vrow == "---"):
			cell.category = "remove"
		elif (vrow.find("->") >= 0):
			if (not removed_column):
				tokens = vrow.split("!")
				full = vrow
				part = (tokens[1] if 1 < python_lib_Builtin.len(tokens) else None)
				if (part is None):
					part = full
				unicode = view.toString(cell.value)
				if (unicode is None):
					unicode = ""
				if (nested or ((unicode.find(part) >= 0))):
					cat = "modify"
					div = part
					if (part != full):
						if nested:
							cell.conflicted = view.hashExists(raw,"theirs")
						else:
							cell.conflicted = (unicode.find(full) >= 0)
						if cell.conflicted:
							div = full
							cat = "conflict"
					cell.updated = True
					cell.separator = div
					cell.pretty_separator = div
					if nested:
						if cell.conflicted:
							tokens = [view.hashGet(raw,"before"), view.hashGet(raw,"ours"), view.hashGet(raw,"theirs")]
						else:
							tokens = [view.hashGet(raw,"before"), view.hashGet(raw,"after")]
					else:
						cell.pretty_value = view.toString(cell.pretty_value)
						if (cell.pretty_value is None):
							cell.pretty_value = ""
						if (cell.pretty_value == div):
							tokens = ["", ""]
						else:
							_this = cell.pretty_value
							if (div == ""):
								tokens = python_lib_Builtin.list(_this)
							else:
								tokens = _this.split(div)
					pretty_tokens = tokens
					if (python_lib_Builtin.len(tokens) >= 2):
						python_internal_ArrayImpl._set(pretty_tokens, 0, DiffRender.markSpaces((tokens[0] if 0 < python_lib_Builtin.len(tokens) else None),(tokens[1] if 1 < python_lib_Builtin.len(tokens) else None)))
						python_internal_ArrayImpl._set(pretty_tokens, 1, DiffRender.markSpaces((tokens[1] if 1 < python_lib_Builtin.len(tokens) else None),(tokens[0] if 0 < python_lib_Builtin.len(tokens) else None)))
					if (python_lib_Builtin.len(tokens) >= 3):
						ref = (pretty_tokens[0] if 0 < python_lib_Builtin.len(pretty_tokens) else None)
						python_internal_ArrayImpl._set(pretty_tokens, 0, DiffRender.markSpaces(ref,(tokens[2] if 2 < python_lib_Builtin.len(tokens) else None)))
						python_internal_ArrayImpl._set(pretty_tokens, 2, DiffRender.markSpaces((tokens[2] if 2 < python_lib_Builtin.len(tokens) else None),ref))
					cell.pretty_separator = "".join(python_lib_Builtin.map(hxunichr,[8594]))
					cell.pretty_value = cell.pretty_separator.join([python_Boot.toString1(x1,'') for x1 in pretty_tokens])
					def _hx_local_5():
						cell.category = cat
						return cell.category
					cell.category_given_tr = _hx_local_5()
					offset1 = None
					if cell.conflicted:
						offset1 = 1
					else:
						offset1 = 0
					cell.lvalue = (tokens[offset1] if offset1 >= 0 and offset1 < python_lib_Builtin.len(tokens) else None)
					cell.rvalue = python_internal_ArrayImpl._get(tokens, (offset1 + 1))
					if cell.conflicted:
						cell.pvalue = (tokens[0] if 0 < python_lib_Builtin.len(tokens) else None)
		if ((x == 0) and ((offset > 0))):
			def _hx_local_6():
				cell.category = "index"
				return cell.category
			cell.category_given_tr = _hx_local_6()

	@staticmethod
	def markSpaces(sl,sr):
		if (sl == sr):
			return sl
		if ((sl is None) or ((sr is None))):
			return sl
		slc = StringTools.replace(sl," ","")
		src = StringTools.replace(sr," ","")
		if (slc != src):
			return sl
		slo = String("")
		il = 0
		ir = 0
		while ((il < python_lib_Builtin.len(sl))):
			cl = None
			if ((il < 0) or ((il >= python_lib_Builtin.len(sl)))):
				cl = ""
			else:
				cl = sl[il]
			cr = ""
			if (ir < python_lib_Builtin.len(sr)):
				if ((ir < 0) or ((ir >= python_lib_Builtin.len(sr)))):
					cr = ""
				else:
					cr = sr[ir]
			if (cl == cr):
				slo = (HxOverrides.stringOrNull(slo) + HxOverrides.stringOrNull(cl))
				il = (il + 1)
				ir = (ir + 1)
			elif (cr == " "):
				ir = (ir + 1)
			else:
				slo = (HxOverrides.stringOrNull(slo) + HxOverrides.stringOrNull("".join(python_lib_Builtin.map(hxunichr,[9251]))))
				il = (il + 1)
		return slo

	@staticmethod
	def renderCell(tab,view,x,y):
		cell = CellInfo()
		corner = view.toString(tab.getCell(0,0))
		off = None
		if (corner == "@:@"):
			off = 1
		else:
			off = 0
		DiffRender.examineCell(x,y,view,tab.getCell(x,y),view.toString(tab.getCell(x,off)),view.toString(tab.getCell(off,y)),corner,cell,off)
		return cell

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.text_to_insert = None
		_hx_o.td_open = None
		_hx_o.td_close = None
		_hx_o.open = None
		_hx_o.pretty_arrows = None
		_hx_o.section = None


DiffRender = _hx_classes.registerClass("DiffRender", fields=["text_to_insert","td_open","td_close","open","pretty_arrows","section"], methods=["usePrettyArrows","insert","beginTable","setSection","beginRow","insertCell","endRow","endTable","html","toString","render","renderTables","sampleCss","completeHtml"], statics=["examineCell","markSpaces","renderCell"])(DiffRender)

class EnumValue(object):
	pass
EnumValue = _hx_classes.registerAbstract("EnumValue")(EnumValue)

class FlatCellBuilder(object):

	def __init__(self,flags):
		self.view = None
		self.separator = None
		self.conflict_separator = None
		self.flags = None
		self.flags = flags

	def needSeparator(self):
		return True

	def setSeparator(self,separator):
		self.separator = separator

	def setConflictSeparator(self,separator):
		self.conflict_separator = separator

	def setView(self,view):
		self.view = view

	def update(self,local,remote):
		return self.view.toDatum(((HxOverrides.stringOrNull(FlatCellBuilder.quoteForDiff(self.view,local)) + HxOverrides.stringOrNull(self.separator)) + HxOverrides.stringOrNull(FlatCellBuilder.quoteForDiff(self.view,remote))))

	def conflict(self,parent,local,remote):
		return ((((HxOverrides.stringOrNull(self.view.toString(parent)) + HxOverrides.stringOrNull(self.conflict_separator)) + HxOverrides.stringOrNull(self.view.toString(local))) + HxOverrides.stringOrNull(self.conflict_separator)) + HxOverrides.stringOrNull(self.view.toString(remote)))

	def marker(self,label):
		return self.view.toDatum(label)

	def links(self,unit,row_like):
		if (self.flags.count_like_a_spreadsheet and (not row_like)):
			return self.view.toDatum(unit.toBase26String())
		return self.view.toDatum(unit.toString())

	@staticmethod
	def quoteForDiff(v,d):
		nil = "NULL"
		if v.equals(d,None):
			return nil
		unicode = v.toString(d)
		score = 0
		_g1 = 0
		_g = python_lib_Builtin.len(unicode)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (HxString.charCodeAt(unicode,score) != 95):
				break
			score = (score + 1)
		if (HxString.substr(unicode,score,None) == nil):
			unicode = ("_" + HxOverrides.stringOrNull(unicode))
		return unicode

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.view = None
		_hx_o.separator = None
		_hx_o.conflict_separator = None
		_hx_o.flags = None


FlatCellBuilder = _hx_classes.registerClass("FlatCellBuilder", fields=["view","separator","conflict_separator","flags"], methods=["needSeparator","setSeparator","setConflictSeparator","setView","update","conflict","marker","links"], statics=["quoteForDiff"], interfaces=[CellBuilder])(FlatCellBuilder)

class Row(object):
	pass
Row = _hx_classes.registerClass("Row", methods=["getRowString","isPreamble"])(Row)

class HighlightPatch(object):

	def __init__(self,source,patch,flags = None):
		self.source = None
		self.patch = None
		self.view = None
		self.sourceView = None
		self.csv = None
		self.header = None
		self.headerPre = None
		self.headerPost = None
		self.headerRename = None
		self.headerMove = None
		self.modifier = None
		self.currentRow = None
		self.payloadCol = None
		self.payloadTop = None
		self.mods = None
		self.cmods = None
		self.rowInfo = None
		self.cellInfo = None
		self.rcOffset = None
		self.indexes = None
		self.sourceInPatchCol = None
		self.patchInSourceCol = None
		self.destInPatchCol = None
		self.patchInDestCol = None
		self.patchInSourceRow = None
		self.lastSourceRow = None
		self.actions = None
		self.rowPermutation = None
		self.rowPermutationRev = None
		self.colPermutation = None
		self.colPermutationRev = None
		self.haveDroppedColumns = None
		self.headerRow = None
		self.preambleRow = None
		self.flags = None
		self.meta_change = None
		self.process_meta = None
		self.prev_meta = None
		self.next_meta = None
		self.finished_columns = None
		self.meta = None
		self.source = source
		self.patch = patch
		self.flags = flags
		if (flags is None):
			self.flags = CompareFlags()
		self.view = patch.getCellView()
		self.sourceView = source.getCellView()
		self.meta = source.getMeta()

	def reset(self):
		self.header = haxe_ds_IntMap()
		self.headerPre = haxe_ds_StringMap()
		self.headerPost = haxe_ds_StringMap()
		self.headerRename = haxe_ds_StringMap()
		self.headerMove = None
		self.modifier = haxe_ds_IntMap()
		self.mods = list()
		self.cmods = list()
		self.csv = Csv()
		self.rcOffset = 0
		self.currentRow = -1
		self.rowInfo = CellInfo()
		self.cellInfo = CellInfo()
		def _hx_local_1():
			def _hx_local_0():
				self.patchInDestCol = None
				return self.patchInDestCol
			self.patchInSourceCol = _hx_local_0()
			return self.patchInSourceCol
		self.sourceInPatchCol = _hx_local_1()
		self.patchInSourceRow = haxe_ds_IntMap()
		self.indexes = None
		self.lastSourceRow = -1
		self.actions = list()
		self.rowPermutation = None
		self.rowPermutationRev = None
		self.colPermutation = None
		self.colPermutationRev = None
		self.haveDroppedColumns = False
		self.headerRow = 0
		self.preambleRow = 0
		self.meta_change = False
		self.process_meta = False
		self.prev_meta = None
		self.next_meta = None
		self.finished_columns = False

	def processMeta(self):
		self.process_meta = True

	def apply(self):
		self.reset()
		if (self.patch.get_width() < 2):
			return True
		if (self.patch.get_height() < 1):
			return True
		self.payloadCol = (1 + self.rcOffset)
		self.payloadTop = self.patch.get_width()
		corner = self.patch.getCellView().toString(self.patch.getCell(0,0))
		if (corner == "@:@"):
			self.rcOffset = 1
		else:
			self.rcOffset = 0
		_g1 = 0
		_g = self.patch.get_height()
		while ((_g1 < _g)):
			r = _g1
			_g1 = (_g1 + 1)
			unicode = self.view.toString(self.patch.getCell(self.rcOffset,r))
			_this = self.actions
			_this.append((unicode if ((unicode is not None)) else ""))
			python_lib_Builtin.len(_this)
		def _hx_local_0():
			self.headerRow = self.rcOffset
			return self.headerRow
		self.preambleRow = _hx_local_0()
		_g11 = 0
		_g2 = self.patch.get_height()
		while ((_g11 < _g2)):
			r1 = _g11
			_g11 = (_g11 + 1)
			self.applyRow(r1)
		self.finishColumns()
		self.finishRows()
		return True

	def needSourceColumns(self):
		if (self.sourceInPatchCol is not None):
			return
		self.sourceInPatchCol = haxe_ds_IntMap()
		self.patchInSourceCol = haxe_ds_IntMap()
		av = self.source.getCellView()
		_g1 = 0
		_g = self.source.get_width()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			name = av.toString(self.source.getCell(i,0))
			at = self.headerPre.h.get(name,None)
			if (at is None):
				continue
			self.sourceInPatchCol.set(i,at)
			self.patchInSourceCol.set(at,i)

	def needDestColumns(self):
		if (self.patchInDestCol is not None):
			return
		self.patchInDestCol = haxe_ds_IntMap()
		self.destInPatchCol = haxe_ds_IntMap()
		_g = 0
		_g1 = self.cmods
		while ((_g < python_lib_Builtin.len(_g1))):
			cmod = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (cmod.patchRow != -1):
				self.patchInDestCol.set(cmod.patchRow,cmod.destRow)
				self.destInPatchCol.set(cmod.destRow,cmod.patchRow)

	def needSourceIndex(self):
		if (self.indexes is not None):
			return
		state = TableComparisonState()
		state.a = self.source
		state.b = self.source
		comp = CompareTable(state)
		comp.storeIndexes()
		comp.run()
		comp.align()
		self.indexes = comp.getIndexes()
		self.needSourceColumns()

	def setMetaProp(self,target,column_name,prop_name,value):
		if (column_name is None):
			return
		if (prop_name is None):
			return
		if (not column_name in target.h):
			value1 = list()
			target.h[column_name] = value1
		change = PropertyChange()
		change.prevName = prop_name
		change.name = prop_name
		if (value == ""):
			value = None
		change.val = value
		_this = target.h.get(column_name,None)
		_this.append(change)
		python_lib_Builtin.len(_this)

	def applyMetaRow(self,code):
		self.needSourceColumns()
		codes = code.split("@")
		prop_name = ""
		if (python_lib_Builtin.len(codes) > 1):
			prop_name = python_internal_ArrayImpl._get(codes, (python_lib_Builtin.len(codes) - 2))
		if (python_lib_Builtin.len(codes) > 0):
			code = python_internal_ArrayImpl._get(codes, (python_lib_Builtin.len(codes) - 1))
		if (self.prev_meta is None):
			self.prev_meta = haxe_ds_StringMap()
		if (self.next_meta is None):
			self.next_meta = haxe_ds_StringMap()
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			txt = self.getDatum(i)
			idx_patch = i
			idx_src = None
			if idx_patch in self.patchInSourceCol.h:
				idx_src = self.patchInSourceCol.h.get(idx_patch,None)
			else:
				idx_src = -1
			prev_name = None
			name = None
			if (idx_src != -1):
				prev_name = self.source.getCell(idx_src,0)
			if idx_patch in self.header.h:
				name = self.header.h.get(idx_patch,None)
			DiffRender.examineCell(0,0,self.view,txt,"",code,"",self.cellInfo)
			if self.cellInfo.updated:
				self.setMetaProp(self.prev_meta,prev_name,prop_name,self.cellInfo.lvalue)
				self.setMetaProp(self.next_meta,name,prop_name,self.cellInfo.rvalue)
			else:
				self.setMetaProp(self.prev_meta,prev_name,prop_name,self.cellInfo.value)
				self.setMetaProp(self.next_meta,name,prop_name,self.cellInfo.value)

	def applyRow(self,r):
		self.currentRow = r
		code = (self.actions[r] if r >= 0 and r < python_lib_Builtin.len(self.actions) else None)
		done = False
		if ((r == 0) and ((self.rcOffset > 0))):
			done = True
		elif (code == "@@"):
			def _hx_local_0():
				self.headerRow = r
				return self.headerRow
			self.preambleRow = _hx_local_0()
			self.applyHeader()
			self.applyAction("@@")
			done = True
		elif (code == "!"):
			def _hx_local_1():
				self.headerRow = r
				return self.headerRow
			self.preambleRow = _hx_local_1()
			self.applyMeta()
			done = True
		elif (code.find("@") == 0):
			self.flags.addWarning((("cannot usefully apply diffs with metadata yet: '" + HxOverrides.stringOrNull(code)) + "'"))
			self.preambleRow = r
			self.applyMetaRow(code)
			if self.process_meta:
				codes = code.split("@")
				if (python_lib_Builtin.len(codes) > 0):
					code = python_internal_ArrayImpl._get(codes, (python_lib_Builtin.len(codes) - 1))
			else:
				self.meta_change = True
				done = True
			self.meta_change = True
			done = True
		if self.process_meta:
			return
		if (not done):
			self.finishColumns()
			if (code == "+++"):
				self.applyAction(code)
			elif (code == "---"):
				self.applyAction(code)
			elif ((code == "+") or ((code == ":"))):
				self.applyAction(code)
			elif (code.find("->") >= 0):
				self.applyAction("->")
			else:
				self.lastSourceRow = -1

	def getDatum(self,c):
		return self.patch.getCell(c,self.currentRow)

	def getString(self,c):
		return self.view.toString(self.getDatum(c))

	def getStringNull(self,c):
		d = self.getDatum(c)
		if (d is None):
			return None
		return self.view.toString(d)

	def applyMeta(self):
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			name = self.getString(i)
			if (name == ""):
				continue
			self.modifier.set(i,name)

	def applyHeader(self):
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			name = self.getString(i)
			if (name == "..."):
				self.modifier.set(i,"...")
				self.haveDroppedColumns = True
				continue
			mod = self.modifier.h.get(i,None)
			move = False
			if (mod is not None):
				if (HxString.charCodeAt(mod,0) == 58):
					move = True
					mod = HxString.substr(mod,1,python_lib_Builtin.len(mod))
			self.header.set(i,name)
			if (mod is not None):
				if (HxString.charCodeAt(mod,0) == 40):
					prev_name = HxString.substr(mod,1,(python_lib_Builtin.len(mod) - 2))
					self.headerPre.h[prev_name] = i
					self.headerPost.h[name] = i
					self.headerRename.h[prev_name] = name
					continue
			if (mod != "+++"):
				self.headerPre.h[name] = i
			if (mod != "---"):
				self.headerPost.h[name] = i
			if move:
				if (self.headerMove is None):
					self.headerMove = haxe_ds_StringMap()
				self.headerMove.h[name] = 1
		if (not self.useMetaForRowChanges()):
			if (self.source.get_height() == 0):
				self.applyAction("+++")

	def lookUp(self,_hx_del = 0):
		if (_hx_del is None):
			_hx_del = 0
		if (self.currentRow + _hx_del) in self.patchInSourceRow.h:
			return self.patchInSourceRow.h.get((self.currentRow + _hx_del),None)
		result = -1
		_hx_local_0 = self
		_hx_local_1 = _hx_local_0.currentRow
		_hx_local_0.currentRow = (_hx_local_1 + _hx_del)
		_hx_local_0.currentRow
		if ((self.currentRow >= 0) and ((self.currentRow < self.patch.get_height()))):
			_g = 0
			_g1 = self.indexes
			while ((_g < python_lib_Builtin.len(_g1))):
				idx = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
				_g = (_g + 1)
				match = idx.queryByContent(self)
				if (match.spot_a == 0):
					continue
				if (match.spot_a == 1):
					result = python_internal_ArrayImpl._get(match.item_a.lst, 0)
					break
				if (self.currentRow > 0):
					prev = self.patchInSourceRow.h.get((self.currentRow - 1),None)
					if (prev is not None):
						lst = match.item_a.lst
						_g2 = 0
						while ((_g2 < python_lib_Builtin.len(lst))):
							row = (lst[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(lst) else None)
							_g2 = (_g2 + 1)
							if (row == ((prev + 1))):
								result = row
								break
		self.patchInSourceRow.set(self.currentRow,result)
		result
		_hx_local_4 = self
		_hx_local_5 = _hx_local_4.currentRow
		_hx_local_4.currentRow = (_hx_local_5 - _hx_del)
		_hx_local_4.currentRow
		return result

	def applyActionExternal(self,code):
		if (code == "@@"):
			return
		rc = RowChange()
		rc.action = code
		self.checkAct()
		if (code != "+++"):
			rc.cond = haxe_ds_StringMap()
		if (code != "---"):
			rc.val = haxe_ds_StringMap()
		have_column = False
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			prev_name = self.header.h.get(i,None)
			name = prev_name
			if prev_name in self.headerRename.h:
				name = self.headerRename.h.get(prev_name,None)
			cact = self.modifier.h.get(i,None)
			if (cact == "..."):
				continue
			if ((name is None) or ((name == ""))):
				continue
			txt = self.csv.parseCell(self.getStringNull(i))
			updated = False
			if self.rowInfo.updated:
				self.getPreString(txt)
				updated = self.cellInfo.updated
			if ((cact == "+++") and ((code != "---"))):
				if ((txt is not None) and ((txt != ""))):
					if (rc.val is None):
						rc.val = haxe_ds_StringMap()
					rc.val.h[name] = txt
					have_column = True
			if updated:
				value = self.csv.parseCell(self.cellInfo.lvalue)
				value1 = value
				rc.cond.h[name] = value1
				value2 = self.csv.parseCell(self.cellInfo.rvalue)
				value3 = value2
				rc.val.h[name] = value3
			elif (code == "+++"):
				if (cact != "---"):
					rc.val.h[name] = txt
			elif ((cact != "+++") and ((cact != "---"))):
				rc.cond.h[name] = txt
		if (rc.action == "+"):
			if (not have_column):
				return
			rc.action = "->"
		self.meta.changeRow(rc)

	def applyAction(self,code):
		if self.useMetaForRowChanges():
			self.applyActionExternal(code)
			return
		mod = HighlightPatchUnit()
		mod.code = code
		mod.add = (code == "+++")
		mod.rem = (code == "---")
		mod.update = (code == "->")
		self.needSourceIndex()
		if (self.lastSourceRow == -1):
			self.lastSourceRow = self.lookUp(-1)
		mod.sourcePrevRow = self.lastSourceRow
		nextAct = python_internal_ArrayImpl._get(self.actions, (self.currentRow + 1))
		if ((nextAct != "+++") and ((nextAct != "..."))):
			mod.sourceNextRow = self.lookUp(1)
		if mod.add:
			if (python_internal_ArrayImpl._get(self.actions, (self.currentRow - 1)) != "+++"):
				if (python_internal_ArrayImpl._get(self.actions, (self.currentRow - 1)) == "@@"):
					mod.sourcePrevRow = 0
					self.lastSourceRow = 0
				else:
					mod.sourcePrevRow = self.lookUp(-1)
			mod.sourceRow = mod.sourcePrevRow
			if (mod.sourceRow != -1):
				mod.sourceRowOffset = 1
		else:
			def _hx_local_0():
				self.lastSourceRow = self.lookUp()
				return self.lastSourceRow
			mod.sourceRow = _hx_local_0()
		if (python_internal_ArrayImpl._get(self.actions, (self.currentRow + 1)) == ""):
			self.lastSourceRow = mod.sourceNextRow
		mod.patchRow = self.currentRow
		if (code == "@@"):
			mod.sourceRow = 0
		_this = self.mods
		_this.append(mod)
		python_lib_Builtin.len(_this)

	def checkAct(self):
		act = self.getString(self.rcOffset)
		if (self.rowInfo.value != act):
			DiffRender.examineCell(0,0,self.view,act,"",act,"",self.rowInfo)

	def getPreString(self,txt):
		self.checkAct()
		if (not self.rowInfo.updated):
			return txt
		DiffRender.examineCell(0,0,self.view,txt,"",self.rowInfo.value,"",self.cellInfo)
		if (not self.cellInfo.updated):
			return txt
		return self.cellInfo.lvalue

	def getRowString(self,c):
		at = self.sourceInPatchCol.h.get(c,None)
		if (at is None):
			return "NOT_FOUND"
		return self.getPreString(self.getString(at))

	def isPreamble(self):
		return (self.currentRow <= self.preambleRow)

	def sortMods(self,a,b):
		if ((b.code == "@@") and ((a.code != "@@"))):
			return 1
		if ((a.code == "@@") and ((b.code != "@@"))):
			return -1
		if (((a.sourceRow == -1) and (not a.add)) and ((b.sourceRow != -1))):
			return 1
		if (((a.sourceRow != -1) and (not b.add)) and ((b.sourceRow == -1))):
			return -1
		if ((a.sourceRow + a.sourceRowOffset) > ((b.sourceRow + b.sourceRowOffset))):
			return 1
		if ((a.sourceRow + a.sourceRowOffset) < ((b.sourceRow + b.sourceRowOffset))):
			return -1
		if (a.patchRow > b.patchRow):
			return 1
		if (a.patchRow < b.patchRow):
			return -1
		return 0

	def processMods(self,rmods,fate,len):
		rmods.sort(key= hx_cmp_to_key(self.sortMods))
		offset = 0
		last = -1
		target = 0
		if (python_lib_Builtin.len(rmods) > 0):
			if ((rmods[0] if 0 < python_lib_Builtin.len(rmods) else None).sourcePrevRow == -1):
				last = 0
		_g = 0
		while ((_g < python_lib_Builtin.len(rmods))):
			mod = (rmods[_g] if _g >= 0 and _g < python_lib_Builtin.len(rmods) else None)
			_g = (_g + 1)
			if (last != -1):
				_g2 = last
				_g1 = (mod.sourceRow + mod.sourceRowOffset)
				while ((_g2 < _g1)):
					i = _g2
					_g2 = (_g2 + 1)
					fate.append((i + offset))
					python_lib_Builtin.len(fate)
					target = (target + 1)
					last = (last + 1)
			if mod.rem:
				fate.append(-1)
				python_lib_Builtin.len(fate)
				offset = (offset - 1)
			elif mod.add:
				mod.destRow = target
				target = (target + 1)
				offset = (offset + 1)
			else:
				mod.destRow = target
			if (mod.sourceRow >= 0):
				last = (mod.sourceRow + mod.sourceRowOffset)
				if mod.rem:
					last = (last + 1)
			elif (mod.add and ((mod.sourceNextRow != -1))):
				last = (mod.sourceNextRow + mod.sourceRowOffset)
			elif (mod.rem or mod.add):
				last = -1
		if (last != -1):
			_g3 = last
			while ((_g3 < len)):
				i1 = _g3
				_g3 = (_g3 + 1)
				fate.append((i1 + offset))
				python_lib_Builtin.len(fate)
				target = (target + 1)
				last = (last + 1)
		return (len + offset)

	def useMetaForColumnChanges(self):
		if (self.meta is None):
			return False
		return self.meta.useForColumnChanges()

	def useMetaForRowChanges(self):
		if (self.meta is None):
			return False
		return self.meta.useForRowChanges()

	def computeOrdering(self,mods,permutation,permutationRev,dim):
		to_unit = haxe_ds_IntMap()
		from_unit = haxe_ds_IntMap()
		meta_from_unit = haxe_ds_IntMap()
		ct = 0
		_g = 0
		while ((_g < python_lib_Builtin.len(mods))):
			mod = (mods[_g] if _g >= 0 and _g < python_lib_Builtin.len(mods) else None)
			_g = (_g + 1)
			if (mod.add or mod.rem):
				continue
			if (mod.sourceRow < 0):
				continue
			if (mod.sourcePrevRow >= 0):
				v = mod.sourceRow
				to_unit.set(mod.sourcePrevRow,v)
				v
				v1 = mod.sourcePrevRow
				from_unit.set(mod.sourceRow,v1)
				v1
				if ((mod.sourcePrevRow + 1) != mod.sourceRow):
					ct = (ct + 1)
			if (mod.sourceNextRow >= 0):
				v2 = mod.sourceNextRow
				to_unit.set(mod.sourceRow,v2)
				v2
				v3 = mod.sourceRow
				from_unit.set(mod.sourceNextRow,v3)
				v3
				if ((mod.sourceRow + 1) != mod.sourceNextRow):
					ct = (ct + 1)
		if (ct > 0):
			cursor = None
			logical = None
			starts = []
			_g1 = 0
			while ((_g1 < dim)):
				i = _g1
				_g1 = (_g1 + 1)
				u = from_unit.h.get(i,None)
				if (u is not None):
					meta_from_unit.set(u,i)
					i
				else:
					starts.append(i)
					python_lib_Builtin.len(starts)
			used = haxe_ds_IntMap()
			len = 0
			_g2 = 0
			while ((_g2 < dim)):
				i1 = _g2
				_g2 = (_g2 + 1)
				if ((logical is not None) and logical in meta_from_unit.h):
					cursor = meta_from_unit.h.get(logical,None)
				else:
					cursor = None
				if (cursor is None):
					v4 = None
					v4 = (None if ((python_lib_Builtin.len(starts) == 0)) else starts.pop(0))
					cursor = v4
					logical = v4
				if (cursor is None):
					cursor = 0
				while (cursor in used.h):
					cursor = (((cursor + 1)) % dim)
				logical = cursor
				permutationRev.append(cursor)
				python_lib_Builtin.len(permutationRev)
				used.set(cursor,1)
				1
			_g11 = 0
			_g3 = python_lib_Builtin.len(permutationRev)
			while ((_g11 < _g3)):
				i2 = _g11
				_g11 = (_g11 + 1)
				python_internal_ArrayImpl._set(permutation, i2, -1)
			_g12 = 0
			_g4 = python_lib_Builtin.len(permutation)
			while ((_g12 < _g4)):
				i3 = _g12
				_g12 = (_g12 + 1)
				python_internal_ArrayImpl._set(permutation, (permutationRev[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(permutationRev) else None), i3)

	def permuteRows(self):
		self.rowPermutation = list()
		self.rowPermutationRev = list()
		self.computeOrdering(self.mods,self.rowPermutation,self.rowPermutationRev,self.source.get_height())

	def fillInNewColumns(self):
		_g = 0
		_g1 = self.cmods
		while ((_g < python_lib_Builtin.len(_g1))):
			cmod = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (not cmod.rem):
				if cmod.add:
					_g2 = 0
					_g3 = self.mods
					while ((_g2 < python_lib_Builtin.len(_g3))):
						mod = (_g3[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g3) else None)
						_g2 = (_g2 + 1)
						if ((mod.patchRow != -1) and ((mod.destRow != -1))):
							d = self.patch.getCell(cmod.patchRow,mod.patchRow)
							self.source.setCell(cmod.destRow,mod.destRow,d)
					hdr = self.header.h.get(cmod.patchRow,None)
					self.source.setCell(cmod.destRow,0,self.view.toDatum(hdr))

	def finishRows(self):
		if self.useMetaForRowChanges():
			return
		if (self.source.get_width() == 0):
			if (self.source.get_height() != 0):
				self.source.resize(0,0)
			return
		fate = list()
		self.permuteRows()
		if (python_lib_Builtin.len(self.rowPermutation) > 0):
			_g = 0
			_g1 = self.mods
			while ((_g < python_lib_Builtin.len(_g1))):
				mod = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
				_g = (_g + 1)
				if (mod.sourceRow >= 0):
					mod.sourceRow = python_internal_ArrayImpl._get(self.rowPermutation, mod.sourceRow)
		if (python_lib_Builtin.len(self.rowPermutation) > 0):
			self.source.insertOrDeleteRows(self.rowPermutation,python_lib_Builtin.len(self.rowPermutation))
		len = self.processMods(self.mods,fate,self.source.get_height())
		self.source.insertOrDeleteRows(fate,len)
		self.needDestColumns()
		_g2 = 0
		_g11 = self.mods
		while ((_g2 < python_lib_Builtin.len(_g11))):
			mod1 = (_g11[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g11) else None)
			_g2 = (_g2 + 1)
			if (not mod1.rem):
				if mod1.add:
					_hx_local_2 = self.headerPost.iterator()
					while (_hx_local_2.hasNext()):
						c = hxnext(_hx_local_2)
						offset = self.patchInDestCol.h.get(c,None)
						if ((offset is not None) and ((offset >= 0))):
							self.source.setCell(offset,mod1.destRow,self.patch.getCell(c,mod1.patchRow))
				elif mod1.update:
					self.currentRow = mod1.patchRow
					self.checkAct()
					if (not self.rowInfo.updated):
						continue
					_hx_local_3 = self.headerPre.iterator()
					while (_hx_local_3.hasNext()):
						c1 = hxnext(_hx_local_3)
						txt = self.view.toString(self.patch.getCell(c1,mod1.patchRow))
						DiffRender.examineCell(0,0,self.view,txt,"",self.rowInfo.value,"",self.cellInfo)
						if (not self.cellInfo.updated):
							continue
						if self.cellInfo.conflicted:
							continue
						d = self.view.toDatum(self.csv.parseCell(self.cellInfo.rvalue))
						offset1 = self.patchInDestCol.h.get(c1,None)
						if ((offset1 is not None) and ((offset1 >= 0))):
							self.source.setCell(self.patchInDestCol.h.get(c1,None),mod1.destRow,d)
		self.fillInNewColumns()
		_g12 = 0
		_g3 = self.source.get_width()
		while ((_g12 < _g3)):
			i = _g12
			_g12 = (_g12 + 1)
			name = self.view.toString(self.source.getCell(i,0))
			next_name = self.headerRename.h.get(name,None)
			if (next_name is None):
				continue
			self.source.setCell(i,0,self.view.toDatum(next_name))

	def permuteColumns(self):
		if (self.headerMove is None):
			return
		self.colPermutation = list()
		self.colPermutationRev = list()
		self.computeOrdering(self.cmods,self.colPermutation,self.colPermutationRev,self.source.get_width())
		if (python_lib_Builtin.len(self.colPermutation) == 0):
			return

	def finishColumns(self):
		if self.finished_columns:
			return
		self.finished_columns = True
		self.needSourceColumns()
		_g1 = self.payloadCol
		_g = self.payloadTop
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			act = self.modifier.h.get(i,None)
			hdr = self.header.h.get(i,None)
			if (act is None):
				act = ""
			if (act == "---"):
				at = -1
				if i in self.patchInSourceCol.h:
					at = self.patchInSourceCol.h.get(i,None)
				mod = HighlightPatchUnit()
				mod.code = act
				mod.rem = True
				mod.sourceRow = at
				mod.patchRow = i
				_this = self.cmods
				_this.append(mod)
				python_lib_Builtin.len(_this)
			elif (act == "+++"):
				mod1 = HighlightPatchUnit()
				mod1.code = act
				mod1.add = True
				prev = -1
				cont = False
				mod1.sourceRow = -1
				if (python_lib_Builtin.len(self.cmods) > 0):
					mod1.sourceRow = python_internal_ArrayImpl._get(self.cmods, (python_lib_Builtin.len(self.cmods) - 1)).sourceRow
				if (mod1.sourceRow != -1):
					mod1.sourceRowOffset = 1
				mod1.patchRow = i
				_this1 = self.cmods
				_this1.append(mod1)
				python_lib_Builtin.len(_this1)
			elif (act != "..."):
				at1 = -1
				if i in self.patchInSourceCol.h:
					at1 = self.patchInSourceCol.h.get(i,None)
				mod2 = HighlightPatchUnit()
				mod2.code = act
				mod2.patchRow = i
				mod2.sourceRow = at1
				_this2 = self.cmods
				_this2.append(mod2)
				python_lib_Builtin.len(_this2)
		at2 = -1
		rat = -1
		_g11 = 0
		_g2 = (python_lib_Builtin.len(self.cmods) - 1)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			icode = (self.cmods[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(self.cmods) else None).code
			if ((icode != "+++") and ((icode != "---"))):
				at2 = (self.cmods[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(self.cmods) else None).sourceRow
			python_internal_ArrayImpl._get(self.cmods, (i1 + 1)).sourcePrevRow = at2
			j = ((python_lib_Builtin.len(self.cmods) - 1) - i1)
			jcode = (self.cmods[j] if j >= 0 and j < python_lib_Builtin.len(self.cmods) else None).code
			if ((jcode != "+++") and ((jcode != "---"))):
				rat = (self.cmods[j] if j >= 0 and j < python_lib_Builtin.len(self.cmods) else None).sourceRow
			python_internal_ArrayImpl._get(self.cmods, (j - 1)).sourceNextRow = rat
		fate = list()
		self.permuteColumns()
		if (self.headerMove is not None):
			if (python_lib_Builtin.len(self.colPermutation) > 0):
				_g3 = 0
				_g12 = self.cmods
				while ((_g3 < python_lib_Builtin.len(_g12))):
					mod3 = (_g12[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(_g12) else None)
					_g3 = (_g3 + 1)
					if (mod3.sourceRow >= 0):
						mod3.sourceRow = python_internal_ArrayImpl._get(self.colPermutation, mod3.sourceRow)
				if (not self.useMetaForColumnChanges()):
					self.source.insertOrDeleteColumns(self.colPermutation,python_lib_Builtin.len(self.colPermutation))
		len = self.processMods(self.cmods,fate,self.source.get_width())
		if (not self.useMetaForColumnChanges()):
			self.source.insertOrDeleteColumns(fate,len)
			return
		changed = False
		_g4 = 0
		_g13 = self.cmods
		while ((_g4 < python_lib_Builtin.len(_g13))):
			mod4 = (_g13[_g4] if _g4 >= 0 and _g4 < python_lib_Builtin.len(_g13) else None)
			_g4 = (_g4 + 1)
			if (mod4.code != ""):
				changed = True
				break
		if (not changed):
			return
		columns = list()
		target = haxe_ds_IntMap()
		def _hx_local_2(x):
			if (x < 0):
				return x
			else:
				return (x + 1)
		inc = _hx_local_2
		_g14 = 0
		_g5 = python_lib_Builtin.len(fate)
		while ((_g14 < _g5)):
			i2 = _g14
			_g14 = (_g14 + 1)
			value = inc((fate[i2] if i2 >= 0 and i2 < python_lib_Builtin.len(fate) else None))
			target.set(i2,value)
		self.needSourceColumns()
		self.needDestColumns()
		_g15 = 1
		_g6 = self.patch.get_width()
		while ((_g15 < _g6)):
			idx_patch = _g15
			_g15 = (_g15 + 1)
			change = ColumnChange()
			idx_src = None
			if idx_patch in self.patchInSourceCol.h:
				idx_src = self.patchInSourceCol.h.get(idx_patch,None)
			else:
				idx_src = -1
			prev_name = None
			name = None
			if (idx_src != -1):
				prev_name = self.source.getCell(idx_src,0)
			if (self.modifier.h.get(idx_patch,None) != "---"):
				if idx_patch in self.header.h:
					name = self.header.h.get(idx_patch,None)
			change.prevName = prev_name
			change.name = name
			if (self.next_meta is not None):
				if name in self.next_meta.h:
					change.props = self.next_meta.h.get(name,None)
			columns.append(change)
			python_lib_Builtin.len(columns)
		self.meta.alterColumns(columns)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.source = None
		_hx_o.patch = None
		_hx_o.view = None
		_hx_o.sourceView = None
		_hx_o.csv = None
		_hx_o.header = None
		_hx_o.headerPre = None
		_hx_o.headerPost = None
		_hx_o.headerRename = None
		_hx_o.headerMove = None
		_hx_o.modifier = None
		_hx_o.currentRow = None
		_hx_o.payloadCol = None
		_hx_o.payloadTop = None
		_hx_o.mods = None
		_hx_o.cmods = None
		_hx_o.rowInfo = None
		_hx_o.cellInfo = None
		_hx_o.rcOffset = None
		_hx_o.indexes = None
		_hx_o.sourceInPatchCol = None
		_hx_o.patchInSourceCol = None
		_hx_o.destInPatchCol = None
		_hx_o.patchInDestCol = None
		_hx_o.patchInSourceRow = None
		_hx_o.lastSourceRow = None
		_hx_o.actions = None
		_hx_o.rowPermutation = None
		_hx_o.rowPermutationRev = None
		_hx_o.colPermutation = None
		_hx_o.colPermutationRev = None
		_hx_o.haveDroppedColumns = None
		_hx_o.headerRow = None
		_hx_o.preambleRow = None
		_hx_o.flags = None
		_hx_o.meta_change = None
		_hx_o.process_meta = None
		_hx_o.prev_meta = None
		_hx_o.next_meta = None
		_hx_o.finished_columns = None
		_hx_o.meta = None


HighlightPatch = _hx_classes.registerClass("HighlightPatch", fields=["source","patch","view","sourceView","csv","header","headerPre","headerPost","headerRename","headerMove","modifier","currentRow","payloadCol","payloadTop","mods","cmods","rowInfo","cellInfo","rcOffset","indexes","sourceInPatchCol","patchInSourceCol","destInPatchCol","patchInDestCol","patchInSourceRow","lastSourceRow","actions","rowPermutation","rowPermutationRev","colPermutation","colPermutationRev","haveDroppedColumns","headerRow","preambleRow","flags","meta_change","process_meta","prev_meta","next_meta","finished_columns","meta"], methods=["reset","processMeta","apply","needSourceColumns","needDestColumns","needSourceIndex","setMetaProp","applyMetaRow","applyRow","getDatum","getString","getStringNull","applyMeta","applyHeader","lookUp","applyActionExternal","applyAction","checkAct","getPreString","getRowString","isPreamble","sortMods","processMods","useMetaForColumnChanges","useMetaForRowChanges","computeOrdering","permuteRows","fillInNewColumns","finishRows","permuteColumns","finishColumns"], interfaces=[Row])(HighlightPatch)

class HighlightPatchUnit(object):

	def __init__(self):
		self.add = None
		self.rem = None
		self.update = None
		self.code = None
		self.sourceRow = None
		self.sourceRowOffset = None
		self.sourcePrevRow = None
		self.sourceNextRow = None
		self.destRow = None
		self.patchRow = None
		self.add = False
		self.rem = False
		self.update = False
		self.sourceRow = -1
		self.sourceRowOffset = 0
		self.sourcePrevRow = -1
		self.sourceNextRow = -1
		self.destRow = -1
		self.patchRow = -1
		self.code = ""

	def toString(self):
		return (((((((((((((("(" + HxOverrides.stringOrNull(self.code)) + " patch ") + Std.string(self.patchRow)) + " source ") + Std.string(self.sourcePrevRow)) + ":") + Std.string(self.sourceRow)) + ":") + Std.string(self.sourceNextRow)) + "+") + Std.string(self.sourceRowOffset)) + " dest ") + Std.string(self.destRow)) + ")")

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.add = None
		_hx_o.rem = None
		_hx_o.update = None
		_hx_o.code = None
		_hx_o.sourceRow = None
		_hx_o.sourceRowOffset = None
		_hx_o.sourcePrevRow = None
		_hx_o.sourceNextRow = None
		_hx_o.destRow = None
		_hx_o.patchRow = None


HighlightPatchUnit = _hx_classes.registerClass("HighlightPatchUnit", fields=["add","rem","update","code","sourceRow","sourceRowOffset","sourcePrevRow","sourceNextRow","destRow","patchRow"], methods=["toString"])(HighlightPatchUnit)

class Index(object):

	def __init__(self,flags):
		self.items = None
		self.keys = None
		self.top_freq = None
		self.height = None
		self.cols = None
		self.v = None
		self.indexed_table = None
		self.hdr = None
		self.ignore_whitespace = None
		self.ignore_case = None
		self.items = haxe_ds_StringMap()
		self.cols = list()
		self.keys = list()
		self.top_freq = 0
		self.height = 0
		self.hdr = 0
		self.ignore_whitespace = False
		self.ignore_case = False
		if (flags is not None):
			self.ignore_whitespace = flags.ignore_whitespace
			self.ignore_case = flags.ignore_case

	def addColumn(self,i):
		_this = self.cols
		_this.append(i)
		python_lib_Builtin.len(_this)

	def indexTable(self,t,hdr):
		self.indexed_table = t
		self.hdr = hdr
		if ((python_lib_Builtin.len(self.keys) != t.get_height()) and ((t.get_height() > 0))):
			python_internal_ArrayImpl._set(self.keys, (t.get_height() - 1), None)
		_g1 = 0
		_g = t.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			key = (self.keys[i] if i >= 0 and i < python_lib_Builtin.len(self.keys) else None)
			if (key is None):
				key = self.toKey(t,i)
				python_internal_ArrayImpl._set(self.keys, i, key)
			item = self.items.h.get(key,None)
			if (item is None):
				item = IndexItem()
				self.items.h[key] = item
			ct = None
			if (item.lst is None):
				item.lst = list()
			_this = item.lst
			_this.append(i)
			python_lib_Builtin.len(_this)
			ct = python_lib_Builtin.len(item.lst)
			if (ct > self.top_freq):
				self.top_freq = ct
		self.height = t.get_height()

	def toKey(self,t,i):
		wide = None
		if (i < self.hdr):
			wide = "_"
		else:
			wide = ""
		if (self.v is None):
			self.v = t.getCellView()
		_g1 = 0
		_g = python_lib_Builtin.len(self.cols)
		while ((_g1 < _g)):
			k = _g1
			_g1 = (_g1 + 1)
			d = t.getCell((self.cols[k] if k >= 0 and k < python_lib_Builtin.len(self.cols) else None),i)
			txt = self.v.toString(d)
			if self.ignore_whitespace:
				txt = StringTools.trim(txt)
			if self.ignore_case:
				txt = txt.lower()
			if (k > 0):
				wide = (HxOverrides.stringOrNull(wide) + " // ")
			if ((((txt is None) or ((txt == ""))) or ((txt == "null"))) or ((txt == "undefined"))):
				continue
			wide = (HxOverrides.stringOrNull(wide) + HxOverrides.stringOrNull(txt))
		return wide

	def toKeyByContent(self,row):
		wide = None
		if row.isPreamble():
			wide = "_"
		else:
			wide = ""
		_g1 = 0
		_g = python_lib_Builtin.len(self.cols)
		while ((_g1 < _g)):
			k = _g1
			_g1 = (_g1 + 1)
			txt = row.getRowString((self.cols[k] if k >= 0 and k < python_lib_Builtin.len(self.cols) else None))
			if self.ignore_whitespace:
				txt = StringTools.trim(txt)
			if self.ignore_case:
				txt = txt.lower()
			if (k > 0):
				wide = (HxOverrides.stringOrNull(wide) + " // ")
			if ((((txt is None) or ((txt == ""))) or ((txt == "null"))) or ((txt == "undefined"))):
				continue
			wide = (HxOverrides.stringOrNull(wide) + HxOverrides.stringOrNull(txt))
		return wide

	def getTable(self):
		return self.indexed_table

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.items = None
		_hx_o.keys = None
		_hx_o.top_freq = None
		_hx_o.height = None
		_hx_o.cols = None
		_hx_o.v = None
		_hx_o.indexed_table = None
		_hx_o.hdr = None
		_hx_o.ignore_whitespace = None
		_hx_o.ignore_case = None


Index = _hx_classes.registerClass("Index", fields=["items","keys","top_freq","height","cols","v","indexed_table","hdr","ignore_whitespace","ignore_case"], methods=["addColumn","indexTable","toKey","toKeyByContent","getTable"])(Index)

class IndexItem(object):

	def __init__(self):
		self.lst = None
		pass

	def add(self,i):
		if (self.lst is None):
			self.lst = list()
		_this = self.lst
		_this.append(i)
		python_lib_Builtin.len(_this)
		return python_lib_Builtin.len(self.lst)

	def length(self):
		return python_lib_Builtin.len(self.lst)

	def value(self):
		return (self.lst[0] if 0 < python_lib_Builtin.len(self.lst) else None)

	def asList(self):
		return self.lst

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.lst = None


IndexItem = _hx_classes.registerClass("IndexItem", fields=["lst"], methods=["add","length","value","asList"])(IndexItem)

class IndexPair(object):

	def __init__(self,flags):
		self.ia = None
		self.ib = None
		self.hdr = None
		self.quality = None
		self.flags = None
		self.flags = flags
		self.ia = Index(flags)
		self.ib = Index(flags)
		self.quality = 0
		self.hdr = 0

	def addColumns(self,ca,cb):
		self.ia.addColumn(ca)
		self.ib.addColumn(cb)

	def indexTables(self,a,b,hdr):
		self.ia.indexTable(a,hdr)
		self.ib.indexTable(b,hdr)
		self.hdr = hdr
		good = 0
		_hx_local_1 = self.ia.items.keys()
		while (_hx_local_1.hasNext()):
			key = hxnext(_hx_local_1)
			item_a = self.ia.items.h.get(key,None)
			spot_a = python_lib_Builtin.len(item_a.lst)
			item_b = self.ib.items.h.get(key,None)
			spot_b = 0
			if (item_b is not None):
				spot_b = python_lib_Builtin.len(item_b.lst)
			if ((spot_a == 1) and ((spot_b == 1))):
				good = (good + 1)
		def _hx_local_2():
			b1 = a.get_height()
			return (1.0 if (python_lib_Math.isnan(1.0)) else (b1 if (python_lib_Math.isnan(b1)) else python_lib_Builtin.max(1.0,b1)))
		self.quality = (good / _hx_local_2())

	def queryByKey(self,ka):
		result = CrossMatch()
		result.item_a = self.ia.items.h.get(ka,None)
		result.item_b = self.ib.items.h.get(ka,None)
		def _hx_local_0():
			result.spot_b = 0
			return result.spot_b
		result.spot_a = _hx_local_0()
		if (ka != ""):
			if (result.item_a is not None):
				result.spot_a = python_lib_Builtin.len(result.item_a.lst)
			if (result.item_b is not None):
				result.spot_b = python_lib_Builtin.len(result.item_b.lst)
		return result

	def queryByContent(self,row):
		result = CrossMatch()
		ka = self.ia.toKeyByContent(row)
		return self.queryByKey(ka)

	def queryLocal(self,row):
		ka = self.ia.toKey(self.ia.getTable(),row)
		return self.queryByKey(ka)

	def localKey(self,row):
		return self.ia.toKey(self.ia.getTable(),row)

	def remoteKey(self,row):
		return self.ib.toKey(self.ib.getTable(),row)

	def getTopFreq(self):
		if (self.ib.top_freq > self.ia.top_freq):
			return self.ib.top_freq
		return self.ia.top_freq

	def getQuality(self):
		return self.quality

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.ia = None
		_hx_o.ib = None
		_hx_o.hdr = None
		_hx_o.quality = None
		_hx_o.flags = None


IndexPair = _hx_classes.registerClass("IndexPair", fields=["ia","ib","hdr","quality","flags"], methods=["addColumns","indexTables","queryByKey","queryByContent","queryLocal","localKey","remoteKey","getTopFreq","getQuality"])(IndexPair)

class Meta(object):
	pass
Meta = _hx_classes.registerClass("Meta", methods=["alterColumns","changeRow","applyFlags","asTable","cloneMeta","useForColumnChanges","useForRowChanges","getRowStream","isNested","isSql","getName"])(Meta)

class JsonTable(object):

	def __init__(self,data,name):
		self.w = None
		self.h = None
		self.columns = None
		self.rows = None
		self.data = None
		self.idx2col = None
		self.name = None
		self.data = data
		self.columns = python_Boot.field(data,"columns")
		self.rows = python_Boot.field(data,"rows")
		self.w = python_lib_Builtin.len(self.columns)
		self.h = python_lib_Builtin.len(self.rows)
		self.idx2col = haxe_ds_IntMap()
		_g1 = 0
		_g = python_lib_Builtin.len(self.columns)
		while ((_g1 < _g)):
			idx = _g1
			_g1 = (_g1 + 1)
			v = (self.columns[idx] if idx >= 0 and idx < python_lib_Builtin.len(self.columns) else None)
			self.idx2col.set(idx,v)
			v
		self.name = name

	def getTable(self):
		return self

	def get_width(self):
		return self.w

	def get_height(self):
		return (self.h + 1)

	def getCell(self,x,y):
		if (y == 0):
			return self.idx2col.h.get(x,None)
		field = self.idx2col.h.get(x,None)
		return python_Boot.field(python_internal_ArrayImpl._get(self.rows, (y - 1)),field)

	def setCell(self,x,y,c):
		haxe_Log.trace("JsonTable is read-only",_hx_AnonObject({'fileName': "JsonTable.hx", 'lineNumber': 52, 'className': "JsonTable", 'methodName': "setCell"}))

	def toString(self):
		return ""

	def getCellView(self):
		return SimpleView()

	def isResizable(self):
		return False

	def resize(self,w,h):
		return False

	def clear(self):
		pass

	def insertOrDeleteRows(self,fate,hfate):
		return False

	def insertOrDeleteColumns(self,fate,wfate):
		return False

	def trimBlank(self):
		return False

	def getData(self):
		return None

	def clone(self):
		return None

	def setMeta(self,meta):
		pass

	def getMeta(self):
		return self

	def create(self):
		return None

	def alterColumns(self,columns):
		return False

	def changeRow(self,rc):
		return False

	def applyFlags(self,flags):
		return False

	def asTable(self):
		return None

	def cloneMeta(self,table = None):
		return None

	def useForColumnChanges(self):
		return False

	def useForRowChanges(self):
		return False

	def getRowStream(self):
		return None

	def isNested(self):
		return False

	def isSql(self):
		return False

	def getName(self):
		return self.name

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.w = None
		_hx_o.h = None
		_hx_o.columns = None
		_hx_o.rows = None
		_hx_o.data = None
		_hx_o.idx2col = None
		_hx_o.name = None


JsonTable = _hx_classes.registerClass("JsonTable", fields=["w","h","columns","rows","data","idx2col","name"], methods=["getTable","get_width","get_height","getCell","setCell","toString","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","getData","clone","setMeta","getMeta","create","alterColumns","changeRow","applyFlags","asTable","cloneMeta","useForColumnChanges","useForRowChanges","getRowStream","isNested","isSql","getName"], interfaces=[Meta,Table])(JsonTable)

class JsonTables(object):

	def __init__(self,json,flags):
		self.db = None
		self.t = None
		self.flags = None
		self.db = json
		names = python_Boot.field(json,"names")
		allowed = None
		count = python_lib_Builtin.len(names)
		if ((flags is not None) and ((flags.tables is not None))):
			allowed = haxe_ds_StringMap()
			_g = 0
			_g1 = flags.tables
			while ((_g < python_lib_Builtin.len(_g1))):
				name = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
				_g = (_g + 1)
				allowed.h[name] = True
			count = 0
			_g2 = 0
			while ((_g2 < python_lib_Builtin.len(names))):
				name1 = (names[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(names) else None)
				_g2 = (_g2 + 1)
				if name1 in allowed.h:
					count = (count + 1)
		self.t = SimpleTable(2, (count + 1))
		self.t.setCell(0,0,"name")
		self.t.setCell(1,0,"table")
		v = self.t.getCellView()
		at = 1
		_g3 = 0
		while ((_g3 < python_lib_Builtin.len(names))):
			name2 = (names[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(names) else None)
			_g3 = (_g3 + 1)
			if (allowed is not None):
				if (not name2 in allowed.h):
					continue
			self.t.setCell(0,at,name2)
			tab = python_Boot.field(self.db,"tables")
			tab = python_Boot.field(tab,name2)
			self.t.setCell(1,at,v.wrapTable(JsonTable(tab, name2)))
			at = (at + 1)

	def getCell(self,x,y):
		return self.t.getCell(x,y)

	def setCell(self,x,y,c):
		pass

	def getCellView(self):
		return self.t.getCellView()

	def isResizable(self):
		return False

	def resize(self,w,h):
		return False

	def clear(self):
		pass

	def insertOrDeleteRows(self,fate,hfate):
		return False

	def insertOrDeleteColumns(self,fate,wfate):
		return False

	def trimBlank(self):
		return False

	def get_width(self):
		return self.t.get_width()

	def get_height(self):
		return self.t.get_height()

	def getData(self):
		return None

	def clone(self):
		return None

	def getMeta(self):
		return SimpleMeta(self, True, True)

	def create(self):
		return None

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.db = None
		_hx_o.t = None
		_hx_o.flags = None


JsonTables = _hx_classes.registerClass("JsonTables", fields=["db","t","flags"], methods=["getCell","setCell","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","get_width","get_height","getData","clone","getMeta","create"], interfaces=[Table])(JsonTables)

class Lambda(object):

	@staticmethod
	def array(it):
		a = list()
		_hx_local_0 = HxOverrides.iterator(it)
		while (_hx_local_0.hasNext()):
			i = hxnext(_hx_local_0)
			a.append(i)
			python_lib_Builtin.len(a)
		return a

	@staticmethod
	def map(it,f):
		l = List()
		_hx_local_0 = HxOverrides.iterator(it)
		while (_hx_local_0.hasNext()):
			x = hxnext(_hx_local_0)
			l.add(f(x))
		return l

	@staticmethod
	def has(it,elt):
		_hx_local_0 = HxOverrides.iterator(it)
		while (_hx_local_0.hasNext()):
			x = hxnext(_hx_local_0)
			if (x == elt):
				return True
		return False


Lambda = _hx_classes.registerClass("Lambda", statics=["array","map","has"])(Lambda)

class List(object):

	def __init__(self):
		self.h = None
		self.q = None
		self.length = None
		self.length = 0

	def add(self,item):
		x = [item]
		if (self.h is None):
			self.h = x
		else:
			python_internal_ArrayImpl._set(self.q, 1, x)
		self.q = x
		_hx_local_0 = self
		_hx_local_1 = _hx_local_0.length
		_hx_local_0.length = (_hx_local_1 + 1)
		_hx_local_1

	def iterator(self):
		return _List_ListIterator(self.h)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None
		_hx_o.q = None
		_hx_o.length = None


List = _hx_classes.registerClass("List", fields=["h","q","length"], methods=["add","iterator"])(List)

class _List_ListIterator(object):

	def __init__(self,head):
		self.head = None
		self.val = None
		self.head = head
		self.val = None

	def hasNext(self):
		return (self.head is not None)

	def __next__(self): return self.next()

	def next(self):
		self.val = (self.head[0] if 0 < python_lib_Builtin.len(self.head) else None)
		self.head = (self.head[1] if 1 < python_lib_Builtin.len(self.head) else None)
		return self.val

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.head = None
		_hx_o.val = None


_List_ListIterator = _hx_classes.registerClass("_List.ListIterator", fields=["head","val"], methods=["hasNext","next"])(_List_ListIterator)

class Merger(object):

	def __init__(self,parent,local,remote,flags):
		self.parent = None
		self.local = None
		self.remote = None
		self.flags = None
		self.order = None
		self.units = None
		self.column_order = None
		self.column_units = None
		self.row_mix_local = None
		self.row_mix_remote = None
		self.column_mix_local = None
		self.column_mix_remote = None
		self.conflicts = None
		self.parent = parent
		self.local = local
		self.remote = remote
		self.flags = flags

	def shuffleDimension(self,dim_units,len,fate,cl,cr):
		at = 0
		_g = 0
		while ((_g < python_lib_Builtin.len(dim_units))):
			cunit = (dim_units[_g] if _g >= 0 and _g < python_lib_Builtin.len(dim_units) else None)
			_g = (_g + 1)
			if (cunit.p < 0):
				if (cunit.l < 0):
					if (cunit.r >= 0):
						cr.set(cunit.r,at)
						at
						at = (at + 1)
				else:
					cl.set(cunit.l,at)
					at
					at = (at + 1)
			elif (cunit.l >= 0):
				if (cunit.r < 0):
					pass
				else:
					cl.set(cunit.l,at)
					at
					at = (at + 1)
		_g1 = 0
		while ((_g1 < len)):
			x = _g1
			_g1 = (_g1 + 1)
			idx = cl.h.get(x,None)
			if (idx is None):
				fate.append(-1)
				python_lib_Builtin.len(fate)
			else:
				fate.append(idx)
				python_lib_Builtin.len(fate)
		return at

	def shuffleColumns(self):
		self.column_mix_local = haxe_ds_IntMap()
		self.column_mix_remote = haxe_ds_IntMap()
		fate = list()
		wfate = self.shuffleDimension(self.column_units,self.local.get_width(),fate,self.column_mix_local,self.column_mix_remote)
		self.local.insertOrDeleteColumns(fate,wfate)

	def shuffleRows(self):
		self.row_mix_local = haxe_ds_IntMap()
		self.row_mix_remote = haxe_ds_IntMap()
		fate = list()
		hfate = self.shuffleDimension(self.units,self.local.get_height(),fate,self.row_mix_local,self.row_mix_remote)
		self.local.insertOrDeleteRows(fate,hfate)

	def apply(self):
		self.conflicts = 0
		ct = Coopy.compareTables3(self.parent,self.local,self.remote)
		align = ct.align()
		self.order = align.toOrder()
		self.units = self.order.getList()
		self.column_order = align.meta.toOrder()
		self.column_units = self.column_order.getList()
		allow_insert = self.flags.allowInsert()
		allow_delete = self.flags.allowDelete()
		allow_update = self.flags.allowUpdate()
		view = self.parent.getCellView()
		_g = 0
		_g1 = self.units
		while ((_g < python_lib_Builtin.len(_g1))):
			row = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (((row.l >= 0) and ((row.r >= 0))) and ((row.p >= 0))):
				_g2 = 0
				_g3 = self.column_units
				while ((_g2 < python_lib_Builtin.len(_g3))):
					col = (_g3[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g3) else None)
					_g2 = (_g2 + 1)
					if (((col.l >= 0) and ((col.r >= 0))) and ((col.p >= 0))):
						pcell = self.parent.getCell(col.p,row.p)
						rcell = self.remote.getCell(col.r,row.r)
						if (not view.equals(pcell,rcell)):
							lcell = self.local.getCell(col.l,row.l)
							if view.equals(pcell,lcell):
								self.local.setCell(col.l,row.l,rcell)
							else:
								self.local.setCell(col.l,row.l,Merger.makeConflictedCell(view,pcell,lcell,rcell))
								_hx_local_2 = self
								_hx_local_3 = _hx_local_2.conflicts
								_hx_local_2.conflicts = (_hx_local_3 + 1)
								_hx_local_3
		self.shuffleColumns()
		self.shuffleRows()
		_hx_local_5 = self.column_mix_remote.keys()
		while (_hx_local_5.hasNext()):
			x = hxnext(_hx_local_5)
			x2 = self.column_mix_remote.h.get(x,None)
			_g4 = 0
			_g11 = self.units
			while ((_g4 < python_lib_Builtin.len(_g11))):
				unit = (_g11[_g4] if _g4 >= 0 and _g4 < python_lib_Builtin.len(_g11) else None)
				_g4 = (_g4 + 1)
				if ((unit.l >= 0) and ((unit.r >= 0))):
					self.local.setCell(x2,self.row_mix_local.h.get(unit.l,None),self.remote.getCell(x,unit.r))
				elif ((unit.p < 0) and ((unit.r >= 0))):
					self.local.setCell(x2,self.row_mix_remote.h.get(unit.r,None),self.remote.getCell(x,unit.r))
		_hx_local_7 = self.row_mix_remote.keys()
		while (_hx_local_7.hasNext()):
			y = hxnext(_hx_local_7)
			y2 = self.row_mix_remote.h.get(y,None)
			_g5 = 0
			_g12 = self.column_units
			while ((_g5 < python_lib_Builtin.len(_g12))):
				unit1 = (_g12[_g5] if _g5 >= 0 and _g5 < python_lib_Builtin.len(_g12) else None)
				_g5 = (_g5 + 1)
				if ((unit1.l >= 0) and ((unit1.r >= 0))):
					self.local.setCell(self.column_mix_local.h.get(unit1.l,None),y2,self.remote.getCell(unit1.r,y))
		return self.conflicts

	@staticmethod
	def makeConflictedCell(view,pcell,lcell,rcell):
		return view.toDatum(((((("((( " + HxOverrides.stringOrNull(view.toString(pcell))) + " ))) ") + HxOverrides.stringOrNull(view.toString(lcell))) + " /// ") + HxOverrides.stringOrNull(view.toString(rcell))))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.parent = None
		_hx_o.local = None
		_hx_o.remote = None
		_hx_o.flags = None
		_hx_o.order = None
		_hx_o.units = None
		_hx_o.column_order = None
		_hx_o.column_units = None
		_hx_o.row_mix_local = None
		_hx_o.row_mix_remote = None
		_hx_o.column_mix_local = None
		_hx_o.column_mix_remote = None
		_hx_o.conflicts = None


Merger = _hx_classes.registerClass("Merger", fields=["parent","local","remote","flags","order","units","column_order","column_units","row_mix_local","row_mix_remote","column_mix_local","column_mix_remote","conflicts"], methods=["shuffleDimension","shuffleColumns","shuffleRows","apply"], statics=["makeConflictedCell"])(Merger)

class Mover(object):

	@staticmethod
	def moveUnits(units):
		isrc = list()
		idest = list()
		len = python_lib_Builtin.len(units)
		ltop = -1
		rtop = -1
		in_src = haxe_ds_IntMap()
		in_dest = haxe_ds_IntMap()
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			unit = (units[i] if i >= 0 and i < python_lib_Builtin.len(units) else None)
			if ((unit.l >= 0) and ((unit.r >= 0))):
				if (ltop < unit.l):
					ltop = unit.l
				if (rtop < unit.r):
					rtop = unit.r
				in_src.set(unit.l,i)
				i
				in_dest.set(unit.r,i)
				i
		v = None
		_g1 = 0
		_g2 = (ltop + 1)
		while ((_g1 < _g2)):
			i1 = _g1
			_g1 = (_g1 + 1)
			v = in_src.h.get(i1,None)
			if (v is not None):
				isrc.append(v)
				python_lib_Builtin.len(isrc)
		_g11 = 0
		_g3 = (rtop + 1)
		while ((_g11 < _g3)):
			i2 = _g11
			_g11 = (_g11 + 1)
			v = in_dest.h.get(i2,None)
			if (v is not None):
				idest.append(v)
				python_lib_Builtin.len(idest)
		return Mover.moveWithoutExtras(isrc,idest)

	@staticmethod
	def move(isrc,idest):
		len = python_lib_Builtin.len(isrc)
		len2 = python_lib_Builtin.len(idest)
		in_src = haxe_ds_IntMap()
		in_dest = haxe_ds_IntMap()
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			in_src.set((isrc[i] if i >= 0 and i < python_lib_Builtin.len(isrc) else None),i)
			i
		_g1 = 0
		while ((_g1 < len2)):
			i1 = _g1
			_g1 = (_g1 + 1)
			in_dest.set((idest[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(idest) else None),i1)
			i1
		src = list()
		dest = list()
		v = None
		_g2 = 0
		while ((_g2 < len)):
			i2 = _g2
			_g2 = (_g2 + 1)
			v = (isrc[i2] if i2 >= 0 and i2 < python_lib_Builtin.len(isrc) else None)
			if v in in_dest.h:
				src.append(v)
				python_lib_Builtin.len(src)
		_g3 = 0
		while ((_g3 < len2)):
			i3 = _g3
			_g3 = (_g3 + 1)
			v = (idest[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(idest) else None)
			if v in in_src.h:
				dest.append(v)
				python_lib_Builtin.len(dest)
		return Mover.moveWithoutExtras(src,dest)

	@staticmethod
	def moveWithoutExtras(src,dest):
		if (python_lib_Builtin.len(src) != python_lib_Builtin.len(dest)):
			return None
		if (python_lib_Builtin.len(src) <= 1):
			return []
		len = python_lib_Builtin.len(src)
		in_src = haxe_ds_IntMap()
		blk_len = haxe_ds_IntMap()
		blk_src_loc = haxe_ds_IntMap()
		blk_dest_loc = haxe_ds_IntMap()
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			in_src.set((src[i] if i >= 0 and i < python_lib_Builtin.len(src) else None),i)
			i
		ct = 0
		in_cursor = -2
		out_cursor = 0
		next = None
		blk = -1
		v = None
		while ((out_cursor < len)):
			v = (dest[out_cursor] if out_cursor >= 0 and out_cursor < python_lib_Builtin.len(dest) else None)
			next = in_src.h.get(v,None)
			if (next != ((in_cursor + 1))):
				blk = v
				ct = 1
				blk_src_loc.set(blk,next)
				blk_dest_loc.set(blk,out_cursor)
			else:
				ct = (ct + 1)
			blk_len.set(blk,ct)
			in_cursor = next
			out_cursor = (out_cursor + 1)
		blks = list()
		_hx_local_2 = blk_len.keys()
		while (_hx_local_2.hasNext()):
			k = hxnext(_hx_local_2)
			blks.append(k)
			python_lib_Builtin.len(blks)
		def _hx_local_3(a,b):
			diff = (blk_len.h.get(b,None) - blk_len.h.get(a,None))
			if (diff != 0):
				return diff
			return (a - b)
		blks.sort(key= hx_cmp_to_key(_hx_local_3))
		moved = list()
		while ((python_lib_Builtin.len(blks) > 0)):
			blk1 = None
			blk1 = (None if ((python_lib_Builtin.len(blks) == 0)) else blks.pop(0))
			blen = python_lib_Builtin.len(blks)
			ref_src_loc = blk_src_loc.h.get(blk1,None)
			ref_dest_loc = blk_dest_loc.h.get(blk1,None)
			i1 = (blen - 1)
			while ((i1 >= 0)):
				blki = (blks[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(blks) else None)
				blki_src_loc = blk_src_loc.h.get(blki,None)
				to_left_src = (blki_src_loc < ref_src_loc)
				to_left_dest = (blk_dest_loc.h.get(blki,None) < ref_dest_loc)
				if (to_left_src != to_left_dest):
					ct1 = blk_len.h.get(blki,None)
					_g1 = 0
					while ((_g1 < ct1)):
						j = _g1
						_g1 = (_g1 + 1)
						moved.append((src[blki_src_loc] if blki_src_loc >= 0 and blki_src_loc < python_lib_Builtin.len(src) else None))
						python_lib_Builtin.len(moved)
						blki_src_loc = (blki_src_loc + 1)
					pos = i1
					if (pos < 0):
						pos = (python_lib_Builtin.len(blks) + pos)
					if (pos < 0):
						pos = 0
					res = blks[pos:(pos + 1)]
					del blks[pos:(pos + 1)]
					res
				i1 = (i1 - 1)
		return moved


Mover = _hx_classes.registerClass("Mover", statics=["moveUnits","move","moveWithoutExtras"])(Mover)

class Ndjson(object):

	def __init__(self,tab):
		self.tab = None
		self.view = None
		self.columns = None
		self.header_row = None
		self.tab = tab
		self.view = tab.getCellView()
		self.header_row = 0

	def renderRow(self,r):
		row = haxe_ds_StringMap()
		_g1 = 0
		_g = self.tab.get_width()
		while ((_g1 < _g)):
			c = _g1
			_g1 = (_g1 + 1)
			key = self.view.toString(self.tab.getCell(c,self.header_row))
			if ((c == 0) and ((self.header_row == 1))):
				key = "@:@"
			value = self.tab.getCell(c,r)
			value1 = value
			row.h[key] = value1
		return haxe_format_JsonPrinter._hx_print(row,None,None)

	def render(self):
		txt = ""
		offset = 0
		if (self.tab.get_height() == 0):
			return txt
		if (self.tab.get_width() == 0):
			return txt
		if (self.tab.getCell(0,0) == "@:@"):
			offset = 1
		self.header_row = offset
		_g1 = (self.header_row + 1)
		_g = self.tab.get_height()
		while ((_g1 < _g)):
			r = _g1
			_g1 = (_g1 + 1)
			txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.renderRow(r)))
			txt = (HxOverrides.stringOrNull(txt) + "\n")
		return txt

	def addRow(self,r,txt):
		json = python_lib_Json.loads(txt,None,None,python_Lib.dictToAnon)
		if (self.columns is None):
			self.columns = haxe_ds_StringMap()
		w = self.tab.get_width()
		h = self.tab.get_height()
		resize = False
		_g = 0
		_g1 = python_Boot.fields(json)
		while ((_g < python_lib_Builtin.len(_g1))):
			name = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (not name in self.columns.h):
				self.columns.h[name] = w
				w = (w + 1)
				resize = True
		if (r >= h):
			h = (r + 1)
			resize = True
		if resize:
			self.tab.resize(w,h)
		_g2 = 0
		_g11 = python_Boot.fields(json)
		while ((_g2 < python_lib_Builtin.len(_g11))):
			name1 = (_g11[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g11) else None)
			_g2 = (_g2 + 1)
			v = python_Boot.field(json,name1)
			c = self.columns.h.get(name1,None)
			self.tab.setCell(c,r,v)

	def addHeaderRow(self,r):
		names = self.columns.keys()
		_hx_local_0 = names
		while (_hx_local_0.hasNext()):
			n = hxnext(_hx_local_0)
			self.tab.setCell(self.columns.h.get(n,None),r,self.view.toDatum(n))

	def parse(self,txt):
		self.columns = None
		rows = txt.split("\n")
		h = python_lib_Builtin.len(rows)
		if (h == 0):
			self.tab.clear()
			return
		if (python_internal_ArrayImpl._get(rows, (h - 1)) == ""):
			h = (h - 1)
		_g = 0
		while ((_g < h)):
			i = _g
			_g = (_g + 1)
			at = ((h - i) - 1)
			self.addRow((at + 1),(rows[at] if at >= 0 and at < python_lib_Builtin.len(rows) else None))
		self.addHeaderRow(0)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.tab = None
		_hx_o.view = None
		_hx_o.columns = None
		_hx_o.header_row = None


Ndjson = _hx_classes.registerClass("Ndjson", fields=["tab","view","columns","header_row"], methods=["renderRow","render","addRow","addHeaderRow","parse"])(Ndjson)

class NestedCellBuilder(object):

	def __init__(self):
		self.view = None
		pass

	def needSeparator(self):
		return False

	def setSeparator(self,separator):
		pass

	def setConflictSeparator(self,separator):
		pass

	def setView(self,view):
		self.view = view

	def update(self,local,remote):
		h = self.view.makeHash()
		self.view.hashSet(h,"before",local)
		self.view.hashSet(h,"after",remote)
		return h

	def conflict(self,parent,local,remote):
		h = self.view.makeHash()
		self.view.hashSet(h,"before",parent)
		self.view.hashSet(h,"ours",local)
		self.view.hashSet(h,"theirs",remote)
		return h

	def marker(self,label):
		return self.view.toDatum(label)

	def negToNull(self,x):
		if (x < 0):
			return None
		return x

	def links(self,unit,row_like):
		h = self.view.makeHash()
		if (unit.p >= -1):
			self.view.hashSet(h,"before",self.negToNull(unit.p))
			self.view.hashSet(h,"ours",self.negToNull(unit.l))
			self.view.hashSet(h,"theirs",self.negToNull(unit.r))
			return h
		self.view.hashSet(h,"before",self.negToNull(unit.l))
		self.view.hashSet(h,"after",self.negToNull(unit.r))
		return h

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.view = None


NestedCellBuilder = _hx_classes.registerClass("NestedCellBuilder", fields=["view"], methods=["needSeparator","setSeparator","setConflictSeparator","setView","update","conflict","marker","negToNull","links"], interfaces=[CellBuilder])(NestedCellBuilder)

class Ordering(object):

	def __init__(self):
		self.order = None
		self.ignore_parent = None
		self.order = list()
		self.ignore_parent = False

	def add(self,l,r,p = -2):
		if (p is None):
			p = -2
		if self.ignore_parent:
			p = -2
		_this = self.order
		x = Unit(l, r, p)
		_this.append(x)
		python_lib_Builtin.len(_this)

	def getList(self):
		return self.order

	def setList(self,lst):
		self.order = lst

	def toString(self):
		txt = ""
		_g1 = 0
		_g = python_lib_Builtin.len(self.order)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (i > 0):
				txt = (HxOverrides.stringOrNull(txt) + ", ")
			txt = (HxOverrides.stringOrNull(txt) + Std.string((self.order[i] if i >= 0 and i < python_lib_Builtin.len(self.order) else None)))
		return txt

	def ignoreParent(self):
		self.ignore_parent = True

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.order = None
		_hx_o.ignore_parent = None


Ordering = _hx_classes.registerClass("Ordering", fields=["order","ignore_parent"], methods=["add","getList","setList","toString","ignoreParent"])(Ordering)

class PropertyChange(object):

	def __init__(self):
		self.prevName = None
		self.name = None
		self.val = None
		pass

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.prevName = None
		_hx_o.name = None
		_hx_o.val = None


PropertyChange = _hx_classes.registerClass("PropertyChange", fields=["prevName","name","val"])(PropertyChange)

class Reflect(object):

	@staticmethod
	def field(o,field):
		return python_Boot.field(o,field)

	@staticmethod
	def setField(o,field,value):
		python_lib_Builtin.setattr(o,(("_hx_" + field) if (field in python_Boot.keywords) else (("_hx_" + field) if (((((python_lib_Builtin.len(field) > 2) and ((python_lib_Builtin.ord(field[0]) == 95))) and ((python_lib_Builtin.ord(field[1]) == 95))) and ((python_lib_Builtin.ord(field[(python_lib_Builtin.len(field) - 1)]) != 95)))) else field)),value)

	@staticmethod
	def isFunction(f):
		return (python_lib_Inspect.isfunction(f) or python_lib_Inspect.ismethod(f))

	@staticmethod
	def compare(a,b):
		if ((a is None) and ((b is None))):
			return 0
		if (a is None):
			return 1
		elif (b is None):
			return -1
		elif (a == b):
			return 0
		elif (a > b):
			return 1
		else:
			return -1


Reflect = _hx_classes.registerClass("Reflect", statics=["field","setField","isFunction","compare"])(Reflect)

class RowChange(object):

	def __init__(self):
		self.cond = None
		self.val = None
		self.conflicting_val = None
		self.conflicting_parent_val = None
		self.conflicted = None
		self.is_key = None
		self.action = None
		pass

	def showMap(self,m):
		if (m is None):
			return "{}"
		txt = ""
		_hx_local_2 = m.keys()
		while (_hx_local_2.hasNext()):
			k = hxnext(_hx_local_2)
			if (txt != ""):
				txt = (HxOverrides.stringOrNull(txt) + ", ")
			v = m.h.get(k,None)
			txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull((((HxOverrides.stringOrNull(k) + "=") + Std.string(v)))))
		return (("{ " + HxOverrides.stringOrNull(txt)) + " }")

	def toString(self):
		return ((((HxOverrides.stringOrNull(self.action) + " ") + HxOverrides.stringOrNull(self.showMap(self.cond))) + " : ") + HxOverrides.stringOrNull(self.showMap(self.val)))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.cond = None
		_hx_o.val = None
		_hx_o.conflicting_val = None
		_hx_o.conflicting_parent_val = None
		_hx_o.conflicted = None
		_hx_o.is_key = None
		_hx_o.action = None


RowChange = _hx_classes.registerClass("RowChange", fields=["cond","val","conflicting_val","conflicting_parent_val","conflicted","is_key","action"], methods=["showMap","toString"])(RowChange)

class RowStream(object):
	pass
RowStream = _hx_classes.registerClass("RowStream", methods=["fetchColumns","fetchRow"])(RowStream)

class SimpleMeta(object):

	def __init__(self,t,has_properties = True,may_be_nested = False):
		if (has_properties is None):
			has_properties = True
		if (may_be_nested is None):
			may_be_nested = False
		self.t = None
		self.name2row = None
		self.name2col = None
		self.has_properties = None
		self.metadata = None
		self.keys = None
		self.row_active = None
		self.row_change_cache = None
		self.may_be_nested = None
		self.t = t
		self.rowChange()
		self.colChange()
		self.has_properties = has_properties
		self.may_be_nested = may_be_nested
		self.metadata = None
		self.keys = None
		self.row_active = False
		self.row_change_cache = None

	def storeRowChanges(self,changes):
		self.row_change_cache = changes
		self.row_active = True

	def rowChange(self):
		self.name2row = None

	def colChange(self):
		self.name2col = None

	def col(self,key):
		if (self.t.get_height() < 1):
			return -1
		if (self.name2col is None):
			self.name2col = haxe_ds_StringMap()
			w = self.t.get_width()
			_g = 0
			while ((_g < w)):
				c = _g
				_g = (_g + 1)
				key1 = self.t.getCell(c,0)
				self.name2col.h[key1] = c
		if (not key in self.name2col.h):
			return -1
		return self.name2col.h.get(key,None)

	def row(self,key):
		if (self.t.get_width() < 1):
			return -1
		if (self.name2row is None):
			self.name2row = haxe_ds_StringMap()
			h = self.t.get_height()
			_g = 1
			while ((_g < h)):
				r = _g
				_g = (_g + 1)
				key1 = self.t.getCell(0,r)
				self.name2row.h[key1] = r
		if (not key in self.name2row.h):
			return -1
		return self.name2row.h.get(key,None)

	def alterColumns(self,columns):
		target = haxe_ds_StringMap()
		wfate = 0
		if self.has_properties:
			target.h["@"] = wfate
			wfate = (wfate + 1)
		_g1 = 0
		_g = python_lib_Builtin.len(columns)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			col = (columns[i] if i >= 0 and i < python_lib_Builtin.len(columns) else None)
			if (col.prevName is not None):
				target.h[col.prevName] = wfate
			if (col.name is not None):
				wfate = (wfate + 1)
		fate = list()
		_g11 = 0
		_g2 = self.t.get_width()
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			targeti = -1
			name = self.t.getCell(i1,0)
			if name in target.h:
				targeti = target.h.get(name,None)
			fate.append(targeti)
			python_lib_Builtin.len(fate)
		self.t.insertOrDeleteColumns(fate,wfate)
		start = None
		if self.has_properties:
			start = 1
		else:
			start = 0
		at = start
		_g12 = 0
		_g3 = python_lib_Builtin.len(columns)
		while ((_g12 < _g3)):
			i2 = _g12
			_g12 = (_g12 + 1)
			col1 = (columns[i2] if i2 >= 0 and i2 < python_lib_Builtin.len(columns) else None)
			if (col1.name is not None):
				if (col1.name != col1.prevName):
					self.t.setCell(at,0,col1.name)
			if (col1.name is not None):
				at = (at + 1)
		if (not self.has_properties):
			return True
		self.colChange()
		at = start
		_g13 = 0
		_g4 = python_lib_Builtin.len(columns)
		while ((_g13 < _g4)):
			i3 = _g13
			_g13 = (_g13 + 1)
			col2 = (columns[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(columns) else None)
			if (col2.name is not None):
				_g21 = 0
				_g31 = col2.props
				while ((_g21 < python_lib_Builtin.len(_g31))):
					prop = (_g31[_g21] if _g21 >= 0 and _g21 < python_lib_Builtin.len(_g31) else None)
					_g21 = (_g21 + 1)
					self.setCell(col2.name,prop.name,prop.val)
			if (col2.name is not None):
				at = (at + 1)
		return True

	def setCell(self,c,r,val):
		ri = self.row(r)
		if (ri == -1):
			return False
		ci = self.col(c)
		if (ci == -1):
			return False
		self.t.setCell(ci,ri,val)
		return True

	def addMetaData(self,column,property,val):
		if (self.metadata is None):
			self.metadata = haxe_ds_StringMap()
			self.keys = haxe_ds_StringMap()
		if (not column in self.metadata.h):
			value = haxe_ds_StringMap()
			self.metadata.h[column] = value
		props = self.metadata.h.get(column,None)
		value1 = val
		value2 = value1
		props.h[property] = value2
		self.keys.h[property] = True

	def asTable(self):
		if (self.has_properties and ((self.metadata is None))):
			return self.t
		if (self.metadata is None):
			return None
		w = self.t.get_width()
		props = list()
		_hx_local_0 = self.keys.keys()
		while (_hx_local_0.hasNext()):
			k = hxnext(_hx_local_0)
			props.append(k)
			python_lib_Builtin.len(props)
		props.sort(key= hx_cmp_to_key(Reflect.compare))
		mt = SimpleTable((w + 1), (python_lib_Builtin.len(props) + 1))
		mt.setCell(0,0,"@")
		_g = 0
		while ((_g < w)):
			x = _g
			_g = (_g + 1)
			name = self.t.getCell(x,0)
			mt.setCell((1 + x),0,name)
			if (not name in self.metadata.h):
				continue
			vals = self.metadata.h.get(name,None)
			_g2 = 0
			_g1 = python_lib_Builtin.len(props)
			while ((_g2 < _g1)):
				i = _g2
				_g2 = (_g2 + 1)
				if (props[i] if i >= 0 and i < python_lib_Builtin.len(props) else None) in vals.h:
					mt.setCell((1 + x),(i + 1),vals.h.get((props[i] if i >= 0 and i < python_lib_Builtin.len(props) else None),None))
		_g11 = 0
		_g3 = python_lib_Builtin.len(props)
		while ((_g11 < _g3)):
			y = _g11
			_g11 = (_g11 + 1)
			mt.setCell(0,(y + 1),(props[y] if y >= 0 and y < python_lib_Builtin.len(props) else None))
		return mt

	def cloneMeta(self,table = None):
		result = SimpleMeta(table)
		if (self.metadata is not None):
			result.keys = haxe_ds_StringMap()
			_hx_local_0 = self.keys.keys()
			while (_hx_local_0.hasNext()):
				k = hxnext(_hx_local_0)
				result.keys.h[k] = True
			result.metadata = haxe_ds_StringMap()
			_hx_local_2 = self.metadata.keys()
			while (_hx_local_2.hasNext()):
				k1 = hxnext(_hx_local_2)
				if (not k1 in self.metadata.h):
					continue
				vals = self.metadata.h.get(k1,None)
				nvals = haxe_ds_StringMap()
				_hx_local_1 = vals.keys()
				while (_hx_local_1.hasNext()):
					p = hxnext(_hx_local_1)
					value = vals.h.get(p,None)
					value1 = value
					nvals.h[p] = value1
				result.metadata.h[k1] = nvals
		return result

	def useForColumnChanges(self):
		return True

	def useForRowChanges(self):
		return self.row_active

	def changeRow(self,rc):
		_this = self.row_change_cache
		_this.append(rc)
		python_lib_Builtin.len(_this)
		return False

	def applyFlags(self,flags):
		return False

	def getRowStream(self):
		return TableStream(self.t)

	def isNested(self):
		return self.may_be_nested

	def isSql(self):
		return False

	def getName(self):
		return None

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.t = None
		_hx_o.name2row = None
		_hx_o.name2col = None
		_hx_o.has_properties = None
		_hx_o.metadata = None
		_hx_o.keys = None
		_hx_o.row_active = None
		_hx_o.row_change_cache = None
		_hx_o.may_be_nested = None


SimpleMeta = _hx_classes.registerClass("SimpleMeta", fields=["t","name2row","name2col","has_properties","metadata","keys","row_active","row_change_cache","may_be_nested"], methods=["storeRowChanges","rowChange","colChange","col","row","alterColumns","setCell","addMetaData","asTable","cloneMeta","useForColumnChanges","useForRowChanges","changeRow","applyFlags","getRowStream","isNested","isSql","getName"], interfaces=[Meta])(SimpleMeta)

class SimpleTable(object):

	def __init__(self,w,h):
		self.data = None
		self.w = None
		self.h = None
		self.meta = None
		self.data = haxe_ds_IntMap()
		self.w = w
		self.h = h
		self.meta = None

	def getTable(self):
		return self

	def get_width(self):
		return self.w

	def get_height(self):
		return self.h

	def getCell(self,x,y):
		return self.data.h.get((x + ((y * self.w))),None)

	def setCell(self,x,y,c):
		value = c
		self.data.set((x + ((y * self.w))),value)

	def toString(self):
		return SimpleTable.tableToString(self)

	def getCellView(self):
		return SimpleView()

	def isResizable(self):
		return True

	def resize(self,w,h):
		self.w = w
		self.h = h
		return True

	def clear(self):
		self.data = haxe_ds_IntMap()

	def insertOrDeleteRows(self,fate,hfate):
		data2 = haxe_ds_IntMap()
		_g1 = 0
		_g = python_lib_Builtin.len(fate)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			j = (fate[i] if i >= 0 and i < python_lib_Builtin.len(fate) else None)
			if (j != -1):
				_g3 = 0
				_g2 = self.w
				while ((_g3 < _g2)):
					c = _g3
					_g3 = (_g3 + 1)
					idx = ((i * self.w) + c)
					if idx in self.data.h:
						value = self.data.h.get(idx,None)
						data2.set(((j * self.w) + c),value)
		self.h = hfate
		self.data = data2
		return True

	def insertOrDeleteColumns(self,fate,wfate):
		data2 = haxe_ds_IntMap()
		_g1 = 0
		_g = python_lib_Builtin.len(fate)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			j = (fate[i] if i >= 0 and i < python_lib_Builtin.len(fate) else None)
			if (j != -1):
				_g3 = 0
				_g2 = self.h
				while ((_g3 < _g2)):
					r = _g3
					_g3 = (_g3 + 1)
					idx = ((r * self.w) + i)
					if idx in self.data.h:
						value = self.data.h.get(idx,None)
						data2.set(((r * wfate) + j),value)
		self.w = wfate
		self.data = data2
		return True

	def trimBlank(self):
		if (self.h == 0):
			return True
		h_test = self.h
		if (h_test >= 3):
			h_test = 3
		view = self.getCellView()
		space = view.toDatum("")
		more = True
		while (more):
			_g1 = 0
			_g = self.get_width()
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				c = self.getCell(i,(self.h - 1))
				if (not ((view.equals(c,space) or ((c is None))))):
					more = False
					break
			if more:
				_hx_local_0 = self
				_hx_local_1 = _hx_local_0.h
				_hx_local_0.h = (_hx_local_1 - 1)
				_hx_local_1
		more = True
		nw = self.w
		while (more):
			if (self.w == 0):
				break
			_g2 = 0
			while ((_g2 < h_test)):
				i1 = _g2
				_g2 = (_g2 + 1)
				c1 = self.getCell((nw - 1),i1)
				if (not ((view.equals(c1,space) or ((c1 is None))))):
					more = False
					break
			if more:
				nw = (nw - 1)
		if (nw == self.w):
			return True
		data2 = haxe_ds_IntMap()
		_g3 = 0
		while ((_g3 < nw)):
			i2 = _g3
			_g3 = (_g3 + 1)
			_g21 = 0
			_g11 = self.h
			while ((_g21 < _g11)):
				r = _g21
				_g21 = (_g21 + 1)
				idx = ((r * self.w) + i2)
				if idx in self.data.h:
					value = self.data.h.get(idx,None)
					data2.set(((r * nw) + i2),value)
		self.w = nw
		self.data = data2
		return True

	def getData(self):
		return None

	def clone(self):
		result = SimpleTable(self.get_width(), self.get_height())
		_g1 = 0
		_g = self.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = 0
			_g2 = self.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				result.setCell(j,i,self.getCell(j,i))
		if (self.meta is not None):
			result.meta = self.meta.cloneMeta(result)
		return result

	def create(self):
		return SimpleTable(self.get_width(), self.get_height())

	def setMeta(self,meta):
		self.meta = meta

	def getMeta(self):
		return self.meta

	@staticmethod
	def tableToString(tab):
		meta = tab.getMeta()
		if (meta is not None):
			stream = meta.getRowStream()
			if (stream is not None):
				x = ""
				cols = stream.fetchColumns()
				_g1 = 0
				_g = python_lib_Builtin.len(cols)
				while ((_g1 < _g)):
					i = _g1
					_g1 = (_g1 + 1)
					if (i > 0):
						x = (HxOverrides.stringOrNull(x) + ",")
					x = (HxOverrides.stringOrNull(x) + HxOverrides.stringOrNull((cols[i] if i >= 0 and i < python_lib_Builtin.len(cols) else None)))
				x = (HxOverrides.stringOrNull(x) + "\n")
				row = stream.fetchRow()
				while ((row is not None)):
					_g11 = 0
					_g2 = python_lib_Builtin.len(cols)
					while ((_g11 < _g2)):
						i1 = _g11
						_g11 = (_g11 + 1)
						if (i1 > 0):
							x = (HxOverrides.stringOrNull(x) + ",")
						x = (HxOverrides.stringOrNull(x) + Std.string(row.h.get((cols[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(cols) else None),None)))
					x = (HxOverrides.stringOrNull(x) + "\n")
					row = stream.fetchRow()
				return x
		x1 = ""
		_g12 = 0
		_g3 = tab.get_height()
		while ((_g12 < _g3)):
			i2 = _g12
			_g12 = (_g12 + 1)
			_g31 = 0
			_g21 = tab.get_width()
			while ((_g31 < _g21)):
				j = _g31
				_g31 = (_g31 + 1)
				if (j > 0):
					x1 = (HxOverrides.stringOrNull(x1) + ",")
				x1 = (HxOverrides.stringOrNull(x1) + Std.string(tab.getCell(j,i2)))
			x1 = (HxOverrides.stringOrNull(x1) + "\n")
		return x1

	@staticmethod
	def tableIsSimilar(tab1,tab2):
		if ((tab1.get_height() == -1) or ((tab2.get_height() == -1))):
			txt1 = SimpleTable.tableToString(tab1)
			txt2 = SimpleTable.tableToString(tab2)
			return (txt1 == txt2)
		if (tab1.get_width() != tab2.get_width()):
			return False
		if (tab1.get_height() != tab2.get_height()):
			return False
		v = tab1.getCellView()
		_g1 = 0
		_g = tab1.get_height()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_g3 = 0
			_g2 = tab1.get_width()
			while ((_g3 < _g2)):
				j = _g3
				_g3 = (_g3 + 1)
				if (not v.equals(tab1.getCell(j,i),tab2.getCell(j,i))):
					return False
		return True

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.data = None
		_hx_o.w = None
		_hx_o.h = None
		_hx_o.meta = None


SimpleTable = _hx_classes.registerClass("SimpleTable", fields=["data","w","h","meta"], methods=["getTable","get_width","get_height","getCell","setCell","toString","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","getData","clone","create","setMeta","getMeta"], statics=["tableToString","tableIsSimilar"], interfaces=[Table])(SimpleTable)

class View(object):
	pass
View = _hx_classes.registerClass("View", methods=["toString","equals","toDatum","makeHash","hashSet","isHash","hashExists","hashGet","isTable","getTable","wrapTable"])(View)

class SimpleView(object):

	def __init__(self):
		pass

	def toString(self,d):
		if (d is None):
			return ""
		return ("" + Std.string(d))

	def equals(self,d1,d2):
		if ((d1 is None) and ((d2 is None))):
			return True
		if ((d1 is None) and ((("" + Std.string(d2)) == ""))):
			return True
		if ((("" + Std.string(d1)) == "") and ((d2 is None))):
			return True
		return (("" + Std.string(d1)) == (("" + Std.string(d2))))

	def toDatum(self,x):
		return x

	def makeHash(self):
		return haxe_ds_StringMap()

	def hashSet(self,h,unicode,d):
		hh = h
		value = d
		value1 = value
		hh.h[unicode] = value1

	def hashExists(self,h,unicode):
		hh = h
		return unicode in hh.h

	def hashGet(self,h,unicode):
		hh = h
		return hh.h.get(unicode,None)

	def isHash(self,h):
		return Std._hx_is(h,haxe_ds_StringMap)

	def isTable(self,t):
		return Std._hx_is(t,Table)

	def getTable(self,t):
		return t

	def wrapTable(self,t):
		return t

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
SimpleView = _hx_classes.registerClass("SimpleView", methods=["toString","equals","toDatum","makeHash","hashSet","hashExists","hashGet","isHash","isTable","getTable","wrapTable"], interfaces=[View])(SimpleView)

class SparseSheet(object):

	def __init__(self):
		self.h = None
		self.w = None
		self.row = None
		self.zero = None
		def _hx_local_0():
			self.w = 0
			return self.w
		self.h = _hx_local_0()

	def resize(self,w,h,zero):
		self.row = haxe_ds_IntMap()
		self.nonDestructiveResize(w,h,zero)

	def nonDestructiveResize(self,w,h,zero):
		self.w = w
		self.h = h
		self.zero = zero

	def get(self,x,y):
		cursor = self.row.h.get(y,None)
		if (cursor is None):
			return self.zero
		val = cursor.h.get(x,None)
		if (val is None):
			return self.zero
		return val

	def set(self,x,y,val):
		cursor = self.row.h.get(y,None)
		if (cursor is None):
			cursor = haxe_ds_IntMap()
			self.row.set(y,cursor)
		cursor.set(x,val)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None
		_hx_o.w = None
		_hx_o.row = None
		_hx_o.zero = None


SparseSheet = _hx_classes.registerClass("SparseSheet", fields=["h","w","row","zero"], methods=["resize","nonDestructiveResize","get","set"])(SparseSheet)

class SqlColumn(object):

	def __init__(self):
		self.name = None
		self.primary = None
		self.type_value = None
		self.type_family = None
		self.name = ""
		self.primary = False
		self.type_value = None
		self.type_family = None

	def setName(self,name):
		self.name = name

	def setPrimaryKey(self,primary):
		self.primary = primary

	def setType(self,value,family):
		self.type_value = value
		self.type_family = family

	def getName(self):
		return self.name

	def isPrimaryKey(self):
		return self.primary

	def toString(self):
		return (HxOverrides.stringOrNull((("*" if (self.primary) else ""))) + HxOverrides.stringOrNull(self.name))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.name = None
		_hx_o.primary = None
		_hx_o.type_value = None
		_hx_o.type_family = None


SqlColumn = _hx_classes.registerClass("SqlColumn", fields=["name","primary","type_value","type_family"], methods=["setName","setPrimaryKey","setType","getName","isPrimaryKey","toString"])(SqlColumn)

class SqlCompare(object):

	def __init__(self,db,local,remote,alt,align = None):
		self.db = None
		self.local = None
		self.remote = None
		self.alt = None
		self.at0 = None
		self.at1 = None
		self.at2 = None
		self.diff_ct = None
		self.align = None
		self.peered = None
		self.alt_peered = None
		self.needed = None
		self.db = db
		self.local = local
		self.remote = remote
		self.alt = alt
		self.align = align
		self.peered = False
		self.alt_peered = False
		if ((local is not None) and ((remote is not None))):
			if (self.remote.getDatabase().getNameForAttachment() is not None):
				if (self.remote.getDatabase().getNameForAttachment() != self.local.getDatabase().getNameForAttachment()):
					local.getDatabase().getHelper().attach(db,"__peer__",self.remote.getDatabase().getNameForAttachment())
					self.peered = True
		if ((self.alt is not None) and ((local is not None))):
			if (self.alt.getDatabase().getNameForAttachment() is not None):
				if (self.alt.getDatabase().getNameForAttachment() != self.local.getDatabase().getNameForAttachment()):
					local.getDatabase().getHelper().attach(db,"__alt__",self.alt.getDatabase().getNameForAttachment())
					self.alt_peered = True

	def equalArray(self,a1,a2):
		if (python_lib_Builtin.len(a1) != python_lib_Builtin.len(a2)):
			return False
		_g1 = 0
		_g = python_lib_Builtin.len(a1)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if ((a1[i] if i >= 0 and i < python_lib_Builtin.len(a1) else None) != (a2[i] if i >= 0 and i < python_lib_Builtin.len(a2) else None)):
				return False
		return True

	def validateSchema(self):
		all_cols1 = []
		key_cols1 = []
		access_error = False
		pk_missing = False
		if (self.local is not None):
			all_cols1 = self.local.getColumnNames()
			key_cols1 = self.local.getPrimaryKey()
			if (python_lib_Builtin.len(all_cols1) == 0):
				access_error = True
			if (python_lib_Builtin.len(key_cols1) == 0):
				pk_missing = True
		all_cols2 = []
		key_cols2 = []
		if (self.remote is not None):
			all_cols2 = self.remote.getColumnNames()
			key_cols2 = self.remote.getPrimaryKey()
			if (python_lib_Builtin.len(all_cols2) == 0):
				access_error = True
			if (python_lib_Builtin.len(key_cols2) == 0):
				pk_missing = True
		all_cols3 = all_cols2
		key_cols3 = key_cols2
		if (self.alt is not None):
			all_cols3 = self.alt.getColumnNames()
			key_cols3 = self.alt.getPrimaryKey()
			if (python_lib_Builtin.len(all_cols3) == 0):
				access_error = True
			if (python_lib_Builtin.len(key_cols3) == 0):
				pk_missing = True
		if access_error:
			raise _HxException("Error accessing SQL table")
		if pk_missing:
			raise _HxException("sql diff not possible when primary key not available")
		pk_change = False
		if ((self.local is not None) and ((self.remote is not None))):
			if (not self.equalArray(key_cols1,key_cols2)):
				pk_change = True
		if ((self.local is not None) and ((self.alt is not None))):
			if (not self.equalArray(key_cols1,key_cols3)):
				pk_change = True
		if pk_change:
			raise _HxException("sql diff not possible when primary key changes")
		return True

	def denull(self,x):
		if (x is None):
			return -1
		return x

	def link(self):
		_hx_local_0 = self
		_hx_local_1 = _hx_local_0.diff_ct
		_hx_local_0.diff_ct = (_hx_local_1 + 1)
		_hx_local_1
		mode = self.db.get(0)
		i0 = self.denull(self.db.get(1))
		i1 = self.denull(self.db.get(2))
		i2 = self.denull(self.db.get(3))
		if (i0 == -3):
			i0 = self.at0
			_hx_local_2 = self
			_hx_local_3 = _hx_local_2.at0
			_hx_local_2.at0 = (_hx_local_3 + 1)
			_hx_local_3
		if (i1 == -3):
			i1 = self.at1
			_hx_local_4 = self
			_hx_local_5 = _hx_local_4.at1
			_hx_local_4.at1 = (_hx_local_5 + 1)
			_hx_local_5
		if (i2 == -3):
			i2 = self.at2
			_hx_local_6 = self
			_hx_local_7 = _hx_local_6.at2
			_hx_local_6.at2 = (_hx_local_7 + 1)
			_hx_local_7
		offset = 4
		if (i0 >= 0):
			_g1 = 0
			_g = self.local.get_width()
			while ((_g1 < _g)):
				x = _g1
				_g1 = (_g1 + 1)
				self.local.setCellCache(x,i0,self.db.get((x + offset)))
			offset = (offset + self.local.get_width())
		if (i1 >= 0):
			_g11 = 0
			_g2 = self.remote.get_width()
			while ((_g11 < _g2)):
				x1 = _g11
				_g11 = (_g11 + 1)
				self.remote.setCellCache(x1,i1,self.db.get((x1 + offset)))
			offset = (offset + self.remote.get_width())
		if (i2 >= 0):
			_g12 = 0
			_g3 = self.alt.get_width()
			while ((_g12 < _g3)):
				x2 = _g12
				_g12 = (_g12 + 1)
				self.alt.setCellCache(x2,i2,self.db.get((x2 + offset)))
		if ((mode == 0) or ((mode == 2))):
			self.align.link(i0,i1)
			self.align.addToOrder(i0,i1)
		if (self.alt is not None):
			if ((mode == 1) or ((mode == 2))):
				self.align.reference.link(i0,i2)
				self.align.reference.addToOrder(i0,i2)

	def linkQuery(self,query,order):
		if self.db.begin(query,None,order):
			while (self.db.read()):
				self.link()
			self.db.end()

	def where(self,txt):
		if (txt == ""):
			return " WHERE 1 = 0"
		return (" WHERE " + HxOverrides.stringOrNull(txt))

	def scanColumns(self,all_cols1,all_cols2,key_cols,present1,present2,align):
		align.meta = Alignment()
		_g1 = 0
		_g = python_lib_Builtin.len(all_cols1)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			key = (all_cols1[i] if i >= 0 and i < python_lib_Builtin.len(all_cols1) else None)
			if key in present2.h:
				align.meta.link(i,present2.h.get(key,None))
			else:
				align.meta.link(i,-1)
		_g11 = 0
		_g2 = python_lib_Builtin.len(all_cols2)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			key1 = (all_cols2[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(all_cols2) else None)
			if (not key1 in present1.h):
				align.meta.link(-1,i1)
		align.meta.range(python_lib_Builtin.len(all_cols1),python_lib_Builtin.len(all_cols2))
		_g3 = 0
		while ((_g3 < python_lib_Builtin.len(key_cols))):
			key2 = (key_cols[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(key_cols) else None)
			_g3 = (_g3 + 1)
			unit = Unit(present1.h.get(key2,None), present2.h.get(key2,None))
			align.addIndexColumns(unit)

	def apply(self):
		if (self.db is None):
			return None
		if (self.align is None):
			self.align = Alignment()
		if (not self.validateSchema()):
			return None
		rowid_name = self.db.rowid()
		key_cols = []
		data_cols = []
		all_cols = []
		all_cols1 = []
		all_cols2 = []
		all_cols3 = []
		common = self.local
		if (self.local is not None):
			key_cols = self.local.getPrimaryKey()
			data_cols = self.local.getAllButPrimaryKey()
			all_cols = self.local.getColumnNames()
			all_cols1 = self.local.getColumnNames()
		if (self.remote is not None):
			all_cols2 = self.remote.getColumnNames()
			if (common is None):
				common = self.remote
		if (self.alt is not None):
			all_cols3 = self.alt.getColumnNames()
			if (common is None):
				common = self.alt
		else:
			all_cols3 = all_cols2
		all_common_cols = list()
		data_common_cols = list()
		present1 = haxe_ds_StringMap()
		present2 = haxe_ds_StringMap()
		present3 = haxe_ds_StringMap()
		present_primary = haxe_ds_StringMap()
		has_column_add = False
		_g1 = 0
		_g = python_lib_Builtin.len(key_cols)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			present_primary.h[(key_cols[i] if i >= 0 and i < python_lib_Builtin.len(key_cols) else None)] = i
		_g11 = 0
		_g2 = python_lib_Builtin.len(all_cols1)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			key = (all_cols1[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(all_cols1) else None)
			present1.h[key] = i1
		_g12 = 0
		_g3 = python_lib_Builtin.len(all_cols2)
		while ((_g12 < _g3)):
			i2 = _g12
			_g12 = (_g12 + 1)
			key1 = (all_cols2[i2] if i2 >= 0 and i2 < python_lib_Builtin.len(all_cols2) else None)
			if (not key1 in present1.h):
				has_column_add = True
			present2.h[key1] = i2
		_g13 = 0
		_g4 = python_lib_Builtin.len(all_cols3)
		while ((_g13 < _g4)):
			i3 = _g13
			_g13 = (_g13 + 1)
			key2 = (all_cols3[i3] if i3 >= 0 and i3 < python_lib_Builtin.len(all_cols3) else None)
			if (not key2 in present1.h):
				has_column_add = True
			present3.h[key2] = i3
			if key2 in present1.h:
				if key2 in present2.h:
					all_common_cols.append(key2)
					python_lib_Builtin.len(all_common_cols)
					if (not key2 in present_primary.h):
						data_common_cols.append(key2)
						python_lib_Builtin.len(data_common_cols)
		self.align.meta = Alignment()
		_g14 = 0
		_g5 = python_lib_Builtin.len(all_cols1)
		while ((_g14 < _g5)):
			i4 = _g14
			_g14 = (_g14 + 1)
			key3 = (all_cols1[i4] if i4 >= 0 and i4 < python_lib_Builtin.len(all_cols1) else None)
			if key3 in present2.h:
				self.align.meta.link(i4,present2.h.get(key3,None))
			else:
				self.align.meta.link(i4,-1)
		_g15 = 0
		_g6 = python_lib_Builtin.len(all_cols2)
		while ((_g15 < _g6)):
			i5 = _g15
			_g15 = (_g15 + 1)
			key4 = (all_cols2[i5] if i5 >= 0 and i5 < python_lib_Builtin.len(all_cols2) else None)
			if (not key4 in present1.h):
				self.align.meta.link(-1,i5)
		self.scanColumns(all_cols1,all_cols2,key_cols,present1,present2,self.align)
		self.align.tables(self.local,self.remote)
		if (self.alt is not None):
			self.scanColumns(all_cols1,all_cols3,key_cols,present1,present3,self.align.reference)
			self.align.reference.tables(self.local,self.alt)
		sql_table1 = ""
		sql_table2 = ""
		sql_table3 = ""
		if (self.local is not None):
			sql_table1 = self.local.getQuotedTableName()
		if (self.remote is not None):
			sql_table2 = self.remote.getQuotedTableName()
		if (self.alt is not None):
			sql_table3 = self.alt.getQuotedTableName()
		if self.peered:
			sql_table1 = ("main." + HxOverrides.stringOrNull(sql_table1))
			sql_table2 = ("__peer__." + HxOverrides.stringOrNull(sql_table2))
		if self.alt_peered:
			sql_table2 = ("__alt__." + HxOverrides.stringOrNull(sql_table3))
		sql_key_cols = ""
		_g16 = 0
		_g7 = python_lib_Builtin.len(key_cols)
		while ((_g16 < _g7)):
			i6 = _g16
			_g16 = (_g16 + 1)
			if (i6 > 0):
				sql_key_cols = (HxOverrides.stringOrNull(sql_key_cols) + ",")
			sql_key_cols = (HxOverrides.stringOrNull(sql_key_cols) + HxOverrides.stringOrNull(common.getQuotedColumnName((key_cols[i6] if i6 >= 0 and i6 < python_lib_Builtin.len(key_cols) else None))))
		sql_all_cols = ""
		_g17 = 0
		_g8 = python_lib_Builtin.len(all_common_cols)
		while ((_g17 < _g8)):
			i7 = _g17
			_g17 = (_g17 + 1)
			if (i7 > 0):
				sql_all_cols = (HxOverrides.stringOrNull(sql_all_cols) + ",")
			sql_all_cols = (HxOverrides.stringOrNull(sql_all_cols) + HxOverrides.stringOrNull(common.getQuotedColumnName((all_common_cols[i7] if i7 >= 0 and i7 < python_lib_Builtin.len(all_common_cols) else None))))
		sql_all_cols1 = ""
		_g18 = 0
		_g9 = python_lib_Builtin.len(all_cols1)
		while ((_g18 < _g9)):
			i8 = _g18
			_g18 = (_g18 + 1)
			if (i8 > 0):
				sql_all_cols1 = (HxOverrides.stringOrNull(sql_all_cols1) + ",")
			sql_all_cols1 = (HxOverrides.stringOrNull(sql_all_cols1) + HxOverrides.stringOrNull(self.local.getQuotedColumnName((all_cols1[i8] if i8 >= 0 and i8 < python_lib_Builtin.len(all_cols1) else None))))
		sql_all_cols2 = ""
		_g19 = 0
		_g10 = python_lib_Builtin.len(all_cols2)
		while ((_g19 < _g10)):
			i9 = _g19
			_g19 = (_g19 + 1)
			if (i9 > 0):
				sql_all_cols2 = (HxOverrides.stringOrNull(sql_all_cols2) + ",")
			sql_all_cols2 = (HxOverrides.stringOrNull(sql_all_cols2) + HxOverrides.stringOrNull(self.remote.getQuotedColumnName((all_cols2[i9] if i9 >= 0 and i9 < python_lib_Builtin.len(all_cols2) else None))))
		sql_all_cols3 = ""
		if (self.alt is not None):
			_g110 = 0
			_g20 = python_lib_Builtin.len(all_cols3)
			while ((_g110 < _g20)):
				i10 = _g110
				_g110 = (_g110 + 1)
				if (i10 > 0):
					sql_all_cols3 = (HxOverrides.stringOrNull(sql_all_cols3) + ",")
				sql_all_cols3 = (HxOverrides.stringOrNull(sql_all_cols3) + HxOverrides.stringOrNull(self.alt.getQuotedColumnName((all_cols3[i10] if i10 >= 0 and i10 < python_lib_Builtin.len(all_cols3) else None))))
		sql_key_match2 = ""
		_g111 = 0
		_g21 = python_lib_Builtin.len(key_cols)
		while ((_g111 < _g21)):
			i11 = _g111
			_g111 = (_g111 + 1)
			if (i11 > 0):
				sql_key_match2 = (HxOverrides.stringOrNull(sql_key_match2) + " AND ")
			n = common.getQuotedColumnName((key_cols[i11] if i11 >= 0 and i11 < python_lib_Builtin.len(key_cols) else None))
			sql_key_match2 = (HxOverrides.stringOrNull(sql_key_match2) + HxOverrides.stringOrNull((((((((HxOverrides.stringOrNull(sql_table1) + ".") + HxOverrides.stringOrNull(n)) + " IS ") + HxOverrides.stringOrNull(sql_table2)) + ".") + HxOverrides.stringOrNull(n)))))
		sql_key_match3 = ""
		if (self.alt is not None):
			_g112 = 0
			_g22 = python_lib_Builtin.len(key_cols)
			while ((_g112 < _g22)):
				i12 = _g112
				_g112 = (_g112 + 1)
				if (i12 > 0):
					sql_key_match3 = (HxOverrides.stringOrNull(sql_key_match3) + " AND ")
				n1 = common.getQuotedColumnName((key_cols[i12] if i12 >= 0 and i12 < python_lib_Builtin.len(key_cols) else None))
				sql_key_match3 = (HxOverrides.stringOrNull(sql_key_match3) + HxOverrides.stringOrNull((((((((HxOverrides.stringOrNull(sql_table1) + ".") + HxOverrides.stringOrNull(n1)) + " IS ") + HxOverrides.stringOrNull(sql_table3)) + ".") + HxOverrides.stringOrNull(n1)))))
		sql_data_mismatch = ""
		_g113 = 0
		_g23 = python_lib_Builtin.len(data_common_cols)
		while ((_g113 < _g23)):
			i13 = _g113
			_g113 = (_g113 + 1)
			if (i13 > 0):
				sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + " OR ")
			n2 = common.getQuotedColumnName((data_common_cols[i13] if i13 >= 0 and i13 < python_lib_Builtin.len(data_common_cols) else None))
			sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + HxOverrides.stringOrNull((((((((HxOverrides.stringOrNull(sql_table1) + ".") + HxOverrides.stringOrNull(n2)) + " IS NOT ") + HxOverrides.stringOrNull(sql_table2)) + ".") + HxOverrides.stringOrNull(n2)))))
		_g114 = 0
		_g24 = python_lib_Builtin.len(all_cols2)
		while ((_g114 < _g24)):
			i14 = _g114
			_g114 = (_g114 + 1)
			key5 = (all_cols2[i14] if i14 >= 0 and i14 < python_lib_Builtin.len(all_cols2) else None)
			if (not key5 in present1.h):
				if (sql_data_mismatch != ""):
					sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + " OR ")
				n3 = common.getQuotedColumnName(key5)
				sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + HxOverrides.stringOrNull(((((HxOverrides.stringOrNull(sql_table2) + ".") + HxOverrides.stringOrNull(n3)) + " IS NOT NULL"))))
		if (self.alt is not None):
			_g115 = 0
			_g25 = python_lib_Builtin.len(data_common_cols)
			while ((_g115 < _g25)):
				i15 = _g115
				_g115 = (_g115 + 1)
				if (python_lib_Builtin.len(sql_data_mismatch) > 0):
					sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + " OR ")
				n4 = common.getQuotedColumnName((data_common_cols[i15] if i15 >= 0 and i15 < python_lib_Builtin.len(data_common_cols) else None))
				sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + HxOverrides.stringOrNull((((((((HxOverrides.stringOrNull(sql_table1) + ".") + HxOverrides.stringOrNull(n4)) + " IS NOT ") + HxOverrides.stringOrNull(sql_table3)) + ".") + HxOverrides.stringOrNull(n4)))))
			_g116 = 0
			_g26 = python_lib_Builtin.len(all_cols3)
			while ((_g116 < _g26)):
				i16 = _g116
				_g116 = (_g116 + 1)
				key6 = (all_cols3[i16] if i16 >= 0 and i16 < python_lib_Builtin.len(all_cols3) else None)
				if (not key6 in present1.h):
					if (sql_data_mismatch != ""):
						sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + " OR ")
					n5 = common.getQuotedColumnName(key6)
					sql_data_mismatch = (HxOverrides.stringOrNull(sql_data_mismatch) + HxOverrides.stringOrNull(((((HxOverrides.stringOrNull(sql_table3) + ".") + HxOverrides.stringOrNull(n5)) + " IS NOT NULL"))))
		sql_dbl_cols = ""
		dbl_cols = []
		_g117 = 0
		_g27 = python_lib_Builtin.len(all_cols1)
		while ((_g117 < _g27)):
			i17 = _g117
			_g117 = (_g117 + 1)
			if (sql_dbl_cols != ""):
				sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + ",")
			buf = ("__coopy_" + Std.string(i17))
			n6 = common.getQuotedColumnName((all_cols1[i17] if i17 >= 0 and i17 < python_lib_Builtin.len(all_cols1) else None))
			sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + HxOverrides.stringOrNull((((((HxOverrides.stringOrNull(sql_table1) + ".") + HxOverrides.stringOrNull(n6)) + " AS ") + HxOverrides.stringOrNull(buf)))))
			dbl_cols.append(buf)
			python_lib_Builtin.len(dbl_cols)
		_g118 = 0
		_g28 = python_lib_Builtin.len(all_cols2)
		while ((_g118 < _g28)):
			i18 = _g118
			_g118 = (_g118 + 1)
			if (sql_dbl_cols != ""):
				sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + ",")
			buf1 = (("__coopy_" + Std.string(i18)) + "b")
			n7 = common.getQuotedColumnName((all_cols2[i18] if i18 >= 0 and i18 < python_lib_Builtin.len(all_cols2) else None))
			sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + HxOverrides.stringOrNull((((((HxOverrides.stringOrNull(sql_table2) + ".") + HxOverrides.stringOrNull(n7)) + " AS ") + HxOverrides.stringOrNull(buf1)))))
			dbl_cols.append(buf1)
			python_lib_Builtin.len(dbl_cols)
		if (self.alt is not None):
			_g119 = 0
			_g29 = python_lib_Builtin.len(all_cols3)
			while ((_g119 < _g29)):
				i19 = _g119
				_g119 = (_g119 + 1)
				if (sql_dbl_cols != ""):
					sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + ",")
				buf2 = (("__coopy_" + Std.string(i19)) + "c")
				n8 = common.getQuotedColumnName((all_cols3[i19] if i19 >= 0 and i19 < python_lib_Builtin.len(all_cols3) else None))
				sql_dbl_cols = (HxOverrides.stringOrNull(sql_dbl_cols) + HxOverrides.stringOrNull((((((HxOverrides.stringOrNull(sql_table3) + ".") + HxOverrides.stringOrNull(n8)) + " AS ") + HxOverrides.stringOrNull(buf2)))))
				dbl_cols.append(buf2)
				python_lib_Builtin.len(dbl_cols)
		sql_order = ""
		_g120 = 0
		_g30 = python_lib_Builtin.len(key_cols)
		while ((_g120 < _g30)):
			i20 = _g120
			_g120 = (_g120 + 1)
			if (i20 > 0):
				sql_order = (HxOverrides.stringOrNull(sql_order) + ",")
			n9 = common.getQuotedColumnName((key_cols[i20] if i20 >= 0 and i20 < python_lib_Builtin.len(key_cols) else None))
			sql_order = (HxOverrides.stringOrNull(sql_order) + HxOverrides.stringOrNull(n9))
		rowid = "-3"
		rowid1 = "-3"
		rowid2 = "-3"
		rowid3 = "-3"
		if (rowid_name is not None):
			rowid = rowid_name
			if (self.local is not None):
				rowid1 = ((HxOverrides.stringOrNull(sql_table1) + ".") + HxOverrides.stringOrNull(rowid_name))
			if (self.remote is not None):
				rowid2 = ((HxOverrides.stringOrNull(sql_table2) + ".") + HxOverrides.stringOrNull(rowid_name))
			if (self.alt is not None):
				rowid3 = ((HxOverrides.stringOrNull(sql_table3) + ".") + HxOverrides.stringOrNull(rowid_name))
		self.at0 = 1
		self.at1 = 1
		self.at2 = 1
		self.diff_ct = 0
		if (self.remote is not None):
			sql_inserts = ((((("SELECT DISTINCT 0 AS __coopy_code, NULL, " + HxOverrides.stringOrNull(rowid)) + " AS rowid, NULL, ") + HxOverrides.stringOrNull(sql_all_cols2)) + " FROM ") + HxOverrides.stringOrNull(sql_table2))
			if (self.local is not None):
				sql_inserts = (HxOverrides.stringOrNull(sql_inserts) + HxOverrides.stringOrNull(((((" WHERE NOT EXISTS (SELECT 1 FROM " + HxOverrides.stringOrNull(sql_table1)) + HxOverrides.stringOrNull(self.where(sql_key_match2))) + ")"))))
			sql_inserts_order = (["__coopy_code", "NULL", "rowid", "NULL"] + all_cols2)
			self.linkQuery(sql_inserts,sql_inserts_order)
		if (self.alt is not None):
			sql_inserts1 = ((((("SELECT DISTINCT 1 AS __coopy_code, NULL, NULL, " + HxOverrides.stringOrNull(rowid)) + " AS rowid, ") + HxOverrides.stringOrNull(sql_all_cols3)) + " FROM ") + HxOverrides.stringOrNull(sql_table3))
			if (self.local is not None):
				sql_inserts1 = (HxOverrides.stringOrNull(sql_inserts1) + HxOverrides.stringOrNull(((((" WHERE NOT EXISTS (SELECT 1 FROM " + HxOverrides.stringOrNull(sql_table1)) + HxOverrides.stringOrNull(self.where(sql_key_match3))) + ")"))))
			sql_inserts_order1 = (["__coopy_code", "NULL", "NULL", "rowid"] + all_cols3)
			self.linkQuery(sql_inserts1,sql_inserts_order1)
		if ((self.local is not None) and ((self.remote is not None))):
			sql_updates = (((("SELECT DISTINCT 2 AS __coopy_code, " + HxOverrides.stringOrNull(rowid1)) + " AS __coopy_rowid0, ") + HxOverrides.stringOrNull(rowid2)) + " AS __coopy_rowid1, ")
			if (self.alt is not None):
				sql_updates = (HxOverrides.stringOrNull(sql_updates) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull(rowid3) + " AS __coopy_rowid2,"))))
			else:
				sql_updates = (HxOverrides.stringOrNull(sql_updates) + " NULL,")
			sql_updates = (HxOverrides.stringOrNull(sql_updates) + HxOverrides.stringOrNull((((HxOverrides.stringOrNull(sql_dbl_cols) + " FROM ") + HxOverrides.stringOrNull(sql_table1)))))
			if (sql_table1 != sql_table2):
				sql_updates = (HxOverrides.stringOrNull(sql_updates) + HxOverrides.stringOrNull(((((" INNER JOIN " + HxOverrides.stringOrNull(sql_table2)) + " ON ") + HxOverrides.stringOrNull(sql_key_match2)))))
			if ((self.alt is not None) and ((sql_table1 != sql_table3))):
				sql_updates = (HxOverrides.stringOrNull(sql_updates) + HxOverrides.stringOrNull(((((" INNER JOIN " + HxOverrides.stringOrNull(sql_table3)) + " ON ") + HxOverrides.stringOrNull(sql_key_match3)))))
			sql_updates = (HxOverrides.stringOrNull(sql_updates) + HxOverrides.stringOrNull(self.where(sql_data_mismatch)))
			sql_updates_order = (["__coopy_code", "__coopy_rowid0", "__coopy_rowid1", "__coopy_rowid2"] + dbl_cols)
			self.linkQuery(sql_updates,sql_updates_order)
		if (self.alt is None):
			if (self.local is not None):
				sql_deletes = ((((("SELECT DISTINCT 0 AS __coopy_code, " + HxOverrides.stringOrNull(rowid)) + " AS rowid, NULL, NULL, ") + HxOverrides.stringOrNull(sql_all_cols1)) + " FROM ") + HxOverrides.stringOrNull(sql_table1))
				if (self.remote is not None):
					sql_deletes = (HxOverrides.stringOrNull(sql_deletes) + HxOverrides.stringOrNull(((((" WHERE NOT EXISTS (SELECT 1 FROM " + HxOverrides.stringOrNull(sql_table2)) + HxOverrides.stringOrNull(self.where(sql_key_match2))) + ")"))))
				sql_deletes_order = (["__coopy_code", "rowid", "NULL", "NULL"] + all_cols1)
				self.linkQuery(sql_deletes,sql_deletes_order)
		if (self.alt is not None):
			sql_deletes1 = (((("SELECT 2 AS __coopy_code, " + HxOverrides.stringOrNull(rowid1)) + " AS __coopy_rowid0, ") + HxOverrides.stringOrNull(rowid2)) + " AS __coopy_rowid1, ")
			sql_deletes1 = (HxOverrides.stringOrNull(sql_deletes1) + HxOverrides.stringOrNull(((HxOverrides.stringOrNull(rowid3) + " AS __coopy_rowid2, "))))
			sql_deletes1 = (HxOverrides.stringOrNull(sql_deletes1) + HxOverrides.stringOrNull(sql_dbl_cols))
			sql_deletes1 = (HxOverrides.stringOrNull(sql_deletes1) + HxOverrides.stringOrNull(((" FROM " + HxOverrides.stringOrNull(sql_table1)))))
			if (self.remote is not None):
				sql_deletes1 = (HxOverrides.stringOrNull(sql_deletes1) + HxOverrides.stringOrNull(((((" LEFT OUTER JOIN " + HxOverrides.stringOrNull(sql_table2)) + " ON ") + HxOverrides.stringOrNull(sql_key_match2)))))
			sql_deletes1 = (HxOverrides.stringOrNull(sql_deletes1) + HxOverrides.stringOrNull(((((" LEFT OUTER JOIN " + HxOverrides.stringOrNull(sql_table3)) + " ON ") + HxOverrides.stringOrNull(sql_key_match3)))))
			sql_deletes1 = (HxOverrides.stringOrNull(sql_deletes1) + " WHERE __coopy_rowid1 IS NULL OR __coopy_rowid2 IS NULL")
			sql_deletes_order1 = (["__coopy_code", "__coopy_rowid0", "__coopy_rowid1", "__coopy_rowid2"] + dbl_cols)
			self.linkQuery(sql_deletes1,sql_deletes_order1)
		if (self.diff_ct == 0):
			self.align.markIdentical()
		return self.align

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.db = None
		_hx_o.local = None
		_hx_o.remote = None
		_hx_o.alt = None
		_hx_o.at0 = None
		_hx_o.at1 = None
		_hx_o.at2 = None
		_hx_o.diff_ct = None
		_hx_o.align = None
		_hx_o.peered = None
		_hx_o.alt_peered = None
		_hx_o.needed = None


SqlCompare = _hx_classes.registerClass("SqlCompare", fields=["db","local","remote","alt","at0","at1","at2","diff_ct","align","peered","alt_peered","needed"], methods=["equalArray","validateSchema","denull","link","linkQuery","where","scanColumns","apply"])(SqlCompare)

class SqlDatabase(object):
	pass
SqlDatabase = _hx_classes.registerClass("SqlDatabase", methods=["getColumns","getQuotedTableName","getQuotedColumnName","begin","beginRow","read","get","end","width","rowid","getHelper","getNameForAttachment"])(SqlDatabase)

class SqlHelper(object):
	pass
SqlHelper = _hx_classes.registerClass("SqlHelper", methods=["getTableNames","countRows","getRowIDs","insert","delete","update","attach","alterColumns"])(SqlHelper)

class SqlTable(object):

	def __init__(self,db,name,helper = None):
		self.db = None
		self.columns = None
		self.name = None
		self.quotedTableName = None
		self.cache = None
		self.columnNames = None
		self.h = None
		self.helper = None
		self.id2rid = None
		self.db = db
		self.name = name
		self.helper = helper
		if (helper is None):
			self.helper = db.getHelper()
		self.cache = haxe_ds_IntMap()
		self.h = -1
		self.id2rid = None
		self.getColumns()

	def getColumns(self):
		if (self.columns is not None):
			return
		if (self.db is None):
			return
		self.columns = self.db.getColumns(self.name)
		self.columnNames = list()
		_g = 0
		_g1 = self.columns
		while ((_g < python_lib_Builtin.len(_g1))):
			col = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			_this = self.columnNames
			x = col.getName()
			_this.append(x)
			python_lib_Builtin.len(_this)

	def getPrimaryKey(self):
		self.getColumns()
		result = list()
		_g = 0
		_g1 = self.columns
		while ((_g < python_lib_Builtin.len(_g1))):
			col = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if (not col.isPrimaryKey()):
				continue
			x = col.getName()
			result.append(x)
			python_lib_Builtin.len(result)
		return result

	def getAllButPrimaryKey(self):
		self.getColumns()
		result = list()
		_g = 0
		_g1 = self.columns
		while ((_g < python_lib_Builtin.len(_g1))):
			col = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
			_g = (_g + 1)
			if col.isPrimaryKey():
				continue
			x = col.getName()
			result.append(x)
			python_lib_Builtin.len(result)
		return result

	def getColumnNames(self):
		self.getColumns()
		return self.columnNames

	def getQuotedTableName(self):
		if (self.quotedTableName is not None):
			return self.quotedTableName
		self.quotedTableName = self.db.getQuotedTableName(self.name)
		return self.quotedTableName

	def getQuotedColumnName(self,name):
		return self.db.getQuotedColumnName(name)

	def getCell(self,x,y):
		if (self.h >= 0):
			y = (y - 1)
			if (y >= 0):
				y = (self.id2rid[y] if y >= 0 and y < python_lib_Builtin.len(self.id2rid) else None)
		elif (y == 0):
			y = -1
		if (y < 0):
			self.getColumns()
			return (self.columns[x] if x >= 0 and x < python_lib_Builtin.len(self.columns) else None).name
		row = self.cache.h.get(y,None)
		if (row is None):
			row = haxe_ds_IntMap()
			self.getColumns()
			self.db.beginRow(self.name,y,self.columnNames)
			while (self.db.read()):
				_g1 = 0
				_g = self.get_width()
				while ((_g1 < _g)):
					i = _g1
					_g1 = (_g1 + 1)
					v = self.db.get(i)
					row.set(i,v)
					v
			self.db.end()
			self.cache.set(y,row)
			row
		this1 = self.cache.h.get(y,None)
		return this1.get(x)

	def setCellCache(self,x,y,c):
		row = self.cache.h.get(y,None)
		if (row is None):
			row = haxe_ds_IntMap()
			self.getColumns()
			self.cache.set(y,row)
			row
		v = c
		row.set(x,v)
		v

	def setCell(self,x,y,c):
		haxe_Log.trace("SqlTable cannot set cells yet",_hx_AnonObject({'fileName': "SqlTable.hx", 'lineNumber': 115, 'className': "SqlTable", 'methodName': "setCell"}))

	def getCellView(self):
		return SimpleView()

	def isResizable(self):
		return False

	def resize(self,w,h):
		return False

	def clear(self):
		pass

	def insertOrDeleteRows(self,fate,hfate):
		return False

	def insertOrDeleteColumns(self,fate,wfate):
		return False

	def trimBlank(self):
		return False

	def get_width(self):
		self.getColumns()
		return python_lib_Builtin.len(self.columns)

	def get_height(self):
		if (self.h >= 0):
			return self.h
		return -1

	def getData(self):
		return None

	def clone(self):
		return None

	def create(self):
		return None

	def getMeta(self):
		return self

	def alterColumns(self,columns):
		result = self.helper.alterColumns(self.db,self.name,columns)
		self.columns = None
		return result

	def changeRow(self,rc):
		if (self.helper is None):
			haxe_Log.trace("No sql helper",_hx_AnonObject({'fileName': "SqlTable.hx", 'lineNumber': 183, 'className': "SqlTable", 'methodName': "changeRow"}))
			return False
		if (rc.action == "+++"):
			return self.helper.insert(self.db,self.name,rc.val)
		elif (rc.action == "---"):
			return self.helper.delete(self.db,self.name,rc.cond)
		elif (rc.action == "->"):
			return self.helper.update(self.db,self.name,rc.cond,rc.val)
		return False

	def asTable(self):
		pct = 3
		self.getColumns()
		w = python_lib_Builtin.len(self.columnNames)
		mt = SimpleTable((w + 1), pct)
		mt.setCell(0,0,"@")
		mt.setCell(0,1,"type")
		mt.setCell(0,2,"key")
		_g = 0
		while ((_g < w)):
			x = _g
			_g = (_g + 1)
			i = (x + 1)
			mt.setCell(i,0,(self.columnNames[x] if x >= 0 and x < python_lib_Builtin.len(self.columnNames) else None))
			mt.setCell(i,1,(self.columns[x] if x >= 0 and x < python_lib_Builtin.len(self.columns) else None).type_value)
			mt.setCell(i,2,("primary" if ((self.columns[x] if x >= 0 and x < python_lib_Builtin.len(self.columns) else None).primary) else ""))
		return mt

	def useForColumnChanges(self):
		return True

	def useForRowChanges(self):
		return True

	def cloneMeta(self,table = None):
		return None

	def applyFlags(self,flags):
		return False

	def getDatabase(self):
		return self.db

	def getRowStream(self):
		self.getColumns()
		self.db.begin((("SELECT * FROM " + HxOverrides.stringOrNull(self.getQuotedTableName())) + " ORDER BY ?"),[self.db.rowid()],self.columnNames)
		return self

	def isNested(self):
		return False

	def isSql(self):
		return True

	def fetchRow(self):
		if self.db.read():
			row = haxe_ds_StringMap()
			_g1 = 0
			_g = python_lib_Builtin.len(self.columnNames)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				v = self.db.get(i)
				value = v
				row.h[(self.columnNames[i] if i >= 0 and i < python_lib_Builtin.len(self.columnNames) else None)] = value
				v
			return row
		self.db.end()
		return None

	def fetchColumns(self):
		self.getColumns()
		return self.columnNames

	def getName(self):
		return self.name.toString()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.db = None
		_hx_o.columns = None
		_hx_o.name = None
		_hx_o.quotedTableName = None
		_hx_o.cache = None
		_hx_o.columnNames = None
		_hx_o.h = None
		_hx_o.helper = None
		_hx_o.id2rid = None


SqlTable = _hx_classes.registerClass("SqlTable", fields=["db","columns","name","quotedTableName","cache","columnNames","h","helper","id2rid"], methods=["getColumns","getPrimaryKey","getAllButPrimaryKey","getColumnNames","getQuotedTableName","getQuotedColumnName","getCell","setCellCache","setCell","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","get_width","get_height","getData","clone","create","getMeta","alterColumns","changeRow","asTable","useForColumnChanges","useForRowChanges","cloneMeta","applyFlags","getDatabase","getRowStream","isNested","isSql","fetchRow","fetchColumns","getName"], interfaces=[RowStream,Meta,Table])(SqlTable)

class SqlTableName(object):

	def __init__(self,name = "",prefix = ""):
		if (name is None):
			name = ""
		if (prefix is None):
			prefix = ""
		self.name = None
		self.prefix = None
		self.name = name
		self.prefix = prefix

	def toString(self):
		if (self.prefix == ""):
			return self.name
		return ((HxOverrides.stringOrNull(self.prefix) + ".") + HxOverrides.stringOrNull(self.name))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.name = None
		_hx_o.prefix = None


SqlTableName = _hx_classes.registerClass("SqlTableName", fields=["name","prefix"], methods=["toString"])(SqlTableName)

class SqlTables(object):

	def __init__(self,db,flags):
		self.db = None
		self.t = None
		self.flags = None
		self.db = db
		helper = self.db.getHelper()
		names = helper.getTableNames(db)
		allowed = None
		count = python_lib_Builtin.len(names)
		if (flags.tables is not None):
			allowed = haxe_ds_StringMap()
			_g = 0
			_g1 = flags.tables
			while ((_g < python_lib_Builtin.len(_g1))):
				name = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
				_g = (_g + 1)
				allowed.h[name] = True
			count = 0
			_g2 = 0
			while ((_g2 < python_lib_Builtin.len(names))):
				name1 = (names[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(names) else None)
				_g2 = (_g2 + 1)
				if name1 in allowed.h:
					count = (count + 1)
		self.t = SimpleTable(2, (count + 1))
		self.t.setCell(0,0,"name")
		self.t.setCell(1,0,"table")
		v = self.t.getCellView()
		at = 1
		_g3 = 0
		while ((_g3 < python_lib_Builtin.len(names))):
			name2 = (names[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(names) else None)
			_g3 = (_g3 + 1)
			if (allowed is not None):
				if (not name2 in allowed.h):
					continue
			self.t.setCell(0,at,name2)
			self.t.setCell(1,at,v.wrapTable(SqlTable(db, SqlTableName(name2))))
			at = (at + 1)

	def getCell(self,x,y):
		return self.t.getCell(x,y)

	def setCell(self,x,y,c):
		pass

	def getCellView(self):
		return self.t.getCellView()

	def isResizable(self):
		return False

	def resize(self,w,h):
		return False

	def clear(self):
		pass

	def insertOrDeleteRows(self,fate,hfate):
		return False

	def insertOrDeleteColumns(self,fate,wfate):
		return False

	def trimBlank(self):
		return False

	def get_width(self):
		return self.t.get_width()

	def get_height(self):
		return self.t.get_height()

	def getData(self):
		return None

	def clone(self):
		return None

	def create(self):
		return None

	def getMeta(self):
		return SimpleMeta(self, True, True)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.db = None
		_hx_o.t = None
		_hx_o.flags = None


SqlTables = _hx_classes.registerClass("SqlTables", fields=["db","t","flags"], methods=["getCell","setCell","getCellView","isResizable","resize","clear","insertOrDeleteRows","insertOrDeleteColumns","trimBlank","get_width","get_height","getData","clone","create","getMeta"], interfaces=[Table])(SqlTables)

class SqliteHelper(object):

	def __init__(self):
		pass

	def getTableNames(self,db):
		q = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
		if (not db.begin(q,None,["name"])):
			return None
		names = list()
		while (db.read()):
			x = db.get(0)
			names.append(x)
			python_lib_Builtin.len(names)
		db.end()
		return names

	def countRows(self,db,name):
		q = ("SELECT COUNT(*) AS ct FROM " + HxOverrides.stringOrNull(db.getQuotedTableName(name)))
		if (not db.begin(q,None,["ct"])):
			return -1
		ct = -1
		while (db.read()):
			ct = db.get(0)
		db.end()
		return ct

	def getRowIDs(self,db,name):
		result = list()
		q = (("SELECT ROWID AS r FROM " + HxOverrides.stringOrNull(db.getQuotedTableName(name))) + " ORDER BY ROWID")
		if (not db.begin(q,None,["r"])):
			return None
		while (db.read()):
			c = db.get(0)
			result.append(c)
			python_lib_Builtin.len(result)
		db.end()
		return result

	def update(self,db,name,conds,vals):
		q = (("UPDATE " + HxOverrides.stringOrNull(db.getQuotedTableName(name))) + " SET ")
		lst = list()
		_hx_local_3 = vals.keys()
		while (_hx_local_3.hasNext()):
			k = hxnext(_hx_local_3)
			if (python_lib_Builtin.len(lst) > 0):
				q = (HxOverrides.stringOrNull(q) + ", ")
			q = (HxOverrides.stringOrNull(q) + HxOverrides.stringOrNull(db.getQuotedColumnName(k)))
			q = (HxOverrides.stringOrNull(q) + " = ?")
			x = vals.h.get(k,None)
			lst.append(x)
			python_lib_Builtin.len(lst)
		val_len = python_lib_Builtin.len(lst)
		q = (HxOverrides.stringOrNull(q) + " WHERE ")
		_hx_local_8 = conds.keys()
		while (_hx_local_8.hasNext()):
			k1 = hxnext(_hx_local_8)
			if (python_lib_Builtin.len(lst) > val_len):
				q = (HxOverrides.stringOrNull(q) + " and ")
			q = (HxOverrides.stringOrNull(q) + HxOverrides.stringOrNull(db.getQuotedColumnName(k1)))
			q = (HxOverrides.stringOrNull(q) + " IS ?")
			x1 = conds.h.get(k1,None)
			lst.append(x1)
			python_lib_Builtin.len(lst)
		if (not db.begin(q,lst,[])):
			haxe_Log.trace("Problem with database update",_hx_AnonObject({'fileName': "SqliteHelper.hx", 'lineNumber': 71, 'className': "SqliteHelper", 'methodName': "update"}))
			return False
		db.end()
		return True

	def delete(self,db,name,conds):
		q = (("DELETE FROM " + HxOverrides.stringOrNull(db.getQuotedTableName(name))) + " WHERE ")
		lst = list()
		_hx_local_3 = conds.keys()
		while (_hx_local_3.hasNext()):
			k = hxnext(_hx_local_3)
			if (python_lib_Builtin.len(lst) > 0):
				q = (HxOverrides.stringOrNull(q) + " and ")
			q = (HxOverrides.stringOrNull(q) + HxOverrides.stringOrNull(db.getQuotedColumnName(k)))
			q = (HxOverrides.stringOrNull(q) + " = ?")
			x = conds.h.get(k,None)
			lst.append(x)
			python_lib_Builtin.len(lst)
		if (not db.begin(q,lst,[])):
			haxe_Log.trace("Problem with database delete",_hx_AnonObject({'fileName': "SqliteHelper.hx", 'lineNumber': 90, 'className': "SqliteHelper", 'methodName': "delete"}))
			return False
		db.end()
		return True

	def insert(self,db,name,vals):
		q = (("INSERT INTO " + HxOverrides.stringOrNull(db.getQuotedTableName(name))) + " (")
		lst = list()
		_hx_local_2 = vals.keys()
		while (_hx_local_2.hasNext()):
			k = hxnext(_hx_local_2)
			if (python_lib_Builtin.len(lst) > 0):
				q = (HxOverrides.stringOrNull(q) + ",")
			q = (HxOverrides.stringOrNull(q) + HxOverrides.stringOrNull(db.getQuotedColumnName(k)))
			x = vals.h.get(k,None)
			lst.append(x)
			python_lib_Builtin.len(lst)
		q = (HxOverrides.stringOrNull(q) + ") VALUES(")
		need_comma = False
		_hx_local_6 = vals.keys()
		while (_hx_local_6.hasNext()):
			k1 = hxnext(_hx_local_6)
			if need_comma:
				q = (HxOverrides.stringOrNull(q) + ",")
			q = (HxOverrides.stringOrNull(q) + "?")
			need_comma = True
		q = (HxOverrides.stringOrNull(q) + ")")
		if (not db.begin(q,lst,[])):
			haxe_Log.trace("Problem with database insert",_hx_AnonObject({'fileName': "SqliteHelper.hx", 'lineNumber': 118, 'className': "SqliteHelper", 'methodName': "insert"}))
			return False
		db.end()
		return True

	def attach(self,db,tag,resource_name):
		tag_present = False
		tag_correct = False
		result = list()
		q = "PRAGMA database_list"
		if (not db.begin(q,None,["seq", "name", "file"])):
			return False
		while (db.read()):
			name = db.get(1)
			if (name == tag):
				tag_present = True
				file = db.get(2)
				if (file == resource_name):
					tag_correct = True
		db.end()
		if tag_present:
			if tag_correct:
				return True
			if (not db.begin((("DETACH `" + HxOverrides.stringOrNull(tag)) + "`"),None,[])):
				haxe_Log.trace(("Failed to detach " + HxOverrides.stringOrNull(tag)),_hx_AnonObject({'fileName': "SqliteHelper.hx", 'lineNumber': 147, 'className': "SqliteHelper", 'methodName': "attach"}))
				return False
			db.end()
		if (not db.begin((("ATTACH ? AS `" + HxOverrides.stringOrNull(tag)) + "`"),[resource_name],[])):
			haxe_Log.trace(((("Failed to attach " + HxOverrides.stringOrNull(resource_name)) + " as ") + HxOverrides.stringOrNull(tag)),_hx_AnonObject({'fileName': "SqliteHelper.hx", 'lineNumber': 154, 'className': "SqliteHelper", 'methodName': "attach"}))
			return False
		db.end()
		return True

	def columnListSql(self,x):
		return ",".join([python_Boot.toString1(x1,'') for x1 in x])

	def fetchSchema(self,db,name):
		tname = db.getQuotedTableName(name)
		query = (("select sql from sqlite_master where name = '" + HxOverrides.stringOrNull(tname)) + "'")
		if (not db.begin(query,None,["sql"])):
			haxe_Log.trace(("Cannot find schema for table " + HxOverrides.stringOrNull(tname)),_hx_AnonObject({'fileName': "SqliteHelper.hx", 'lineNumber': 169, 'className': "SqliteHelper", 'methodName': "fetchSchema"}))
			return None
		sql = ""
		if db.read():
			sql = db.get(0)
		db.end()
		return sql

	def splitSchema(self,db,name,sql):
		preamble = ""
		parts = list()
		double_quote = False
		single_quote = False
		token = ""
		nesting = 0
		_g1 = 0
		_g = python_lib_Builtin.len(sql)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ch = None
			if ((i < 0) or ((i >= python_lib_Builtin.len(sql)))):
				ch = ""
			else:
				ch = sql[i]
			if (double_quote or single_quote):
				if double_quote:
					if (ch == "\""):
						double_quote = False
				if single_quote:
					if (ch == "'"):
						single_quote = False
				token = (HxOverrides.stringOrNull(token) + HxOverrides.stringOrNull(ch))
				continue
			brk = False
			if (ch == "("):
				nesting = (nesting + 1)
				if (nesting == 1):
					brk = True
			elif (ch == ")"):
				nesting = (nesting - 1)
				if (nesting == 0):
					brk = True
			if (ch == ","):
				brk = True
				if (nesting == 1):
					pass
			if brk:
				if ((("" if ((0 >= python_lib_Builtin.len(token))) else token[0])) == " "):
					token = HxString.substr(token,1,python_lib_Builtin.len(token))
				if (preamble == ""):
					preamble = token
				else:
					parts.append(token)
					python_lib_Builtin.len(parts)
				token = ""
			else:
				token = (HxOverrides.stringOrNull(token) + HxOverrides.stringOrNull(ch))
		cols = db.getColumns(name)
		name2part = haxe_ds_StringMap()
		name2col = haxe_ds_StringMap()
		_g11 = 0
		_g2 = python_lib_Builtin.len(cols)
		while ((_g11 < _g2)):
			i1 = _g11
			_g11 = (_g11 + 1)
			col = (cols[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(cols) else None)
			name2part.h[col.name] = (parts[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(parts) else None)
			name2col.h[col.name] = (cols[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(cols) else None)
		return _hx_AnonObject({'preamble': preamble, 'parts': parts, 'name2part': name2part, 'columns': cols, 'name2column': name2col})

	def _hx_exec(self,db,query):
		if (not db.begin(query)):
			haxe_Log.trace("database problem",_hx_AnonObject({'fileName': "SqliteHelper.hx", 'lineNumber': 250, 'className': "SqliteHelper", 'methodName': "exec"}))
			return False
		db.end()
		return True

	def alterColumns(self,db,name,columns):
		def _hx_local_0(x):
			if (((x is None) or ((x == ""))) or ((x == "null"))):
				return False
			return True
		notBlank = _hx_local_0
		sql = self.fetchSchema(db,name)
		schema = self.splitSchema(db,name,sql)
		parts = schema.parts
		nparts = list()
		new_column_list = list()
		ins_column_list = list()
		sel_column_list = list()
		meta = schema.columns
		_g1 = 0
		_g = python_lib_Builtin.len(columns)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			c = (columns[i] if i >= 0 and i < python_lib_Builtin.len(columns) else None)
			if (c.name is not None):
				if (c.prevName is not None):
					sel_column_list.append(c.prevName)
					python_lib_Builtin.len(sel_column_list)
					ins_column_list.append(c.name)
					python_lib_Builtin.len(ins_column_list)
				orig_type = ""
				orig_primary = False
				if c.name in schema.name2column.h:
					m = schema.name2column.h.get(c.name,None)
					orig_type = m.type_value
					orig_primary = m.primary
				next_type = orig_type
				next_primary = orig_primary
				if (c.props is not None):
					_g2 = 0
					_g3 = c.props
					while ((_g2 < python_lib_Builtin.len(_g3))):
						p = (_g3[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g3) else None)
						_g2 = (_g2 + 1)
						if (p.name == "type"):
							next_type = p.val
						if (p.name == "key"):
							next_primary = (("" + Std.string(p.val)) == "primary")
				part = ("" + HxOverrides.stringOrNull(c.name))
				if notBlank(next_type):
					part = (HxOverrides.stringOrNull(part) + HxOverrides.stringOrNull(((" " + HxOverrides.stringOrNull(next_type)))))
				if next_primary:
					part = (HxOverrides.stringOrNull(part) + " PRIMARY KEY")
				nparts.append(part)
				python_lib_Builtin.len(nparts)
				new_column_list.append(c.name)
				python_lib_Builtin.len(new_column_list)
		if (not self._hx_exec(db,"BEGIN TRANSACTION")):
			return False
		c1 = self.columnListSql(ins_column_list)
		tname = db.getQuotedTableName(name)
		if (not self._hx_exec(db,(("CREATE TEMPORARY TABLE __coopy_backup(" + HxOverrides.stringOrNull(c1)) + ")"))):
			return False
		if (not self._hx_exec(db,((((("INSERT INTO __coopy_backup (" + HxOverrides.stringOrNull(c1)) + ") SELECT ") + HxOverrides.stringOrNull(c1)) + " FROM ") + HxOverrides.stringOrNull(tname)))):
			return False
		if (not self._hx_exec(db,("DROP TABLE " + HxOverrides.stringOrNull(tname)))):
			return False
		if (not self._hx_exec(db,(((HxOverrides.stringOrNull(schema.preamble) + "(") + HxOverrides.stringOrNull(", ".join([python_Boot.toString1(x1,'') for x1 in nparts]))) + ")"))):
			return False
		if (not self._hx_exec(db,(((((("INSERT INTO " + HxOverrides.stringOrNull(tname)) + " (") + HxOverrides.stringOrNull(c1)) + ") SELECT ") + HxOverrides.stringOrNull(c1)) + " FROM __coopy_backup"))):
			return False
		if (not self._hx_exec(db,"DROP TABLE __coopy_backup")):
			return False
		if (not self._hx_exec(db,"COMMIT")):
			return False
		return True

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
SqliteHelper = _hx_classes.registerClass("SqliteHelper", methods=["getTableNames","countRows","getRowIDs","update","delete","insert","attach","columnListSql","fetchSchema","splitSchema","exec","alterColumns"], interfaces=[SqlHelper])(SqliteHelper)

class Std(object):

	@staticmethod
	def _hx_is(v,t):
		if ((v is None) and ((t is None))):
			return False
		if (t is None):
			return False
		if (t == Dynamic):
			return True
		isBool = python_lib_Builtin.isinstance(v,python_lib_Builtin.bool)
		if ((t == Bool) and isBool):
			return True
		if ((((not isBool) and (not (t == Bool))) and (t == Int)) and python_lib_Builtin.isinstance(v,python_lib_Builtin.int)):
			return True
		vIsFloat = python_lib_Builtin.isinstance(v,python_lib_Builtin.float)
		def _hx_local_0():
			f = v
			return (((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))
		def _hx_local_1():
			x = v
			def _hx_local_4():
				def _hx_local_3():
					_hx_local_2 = None
					try:
						_hx_local_2 = python_lib_Builtin.int(x)
					except Exception as _hx_e:
						_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
						e = _hx_e1
						_hx_local_2 = None
					return _hx_local_2
				return _hx_local_3()
			return _hx_local_4()
		if (((((((not isBool) and vIsFloat) and (t == Int)) and _hx_local_0()) and ((v == _hx_local_1()))) and ((v <= 2147483647))) and ((v >= -2147483648))):
			return True
		if (((not isBool) and (t == Float)) and python_lib_Builtin.isinstance(v,(float,int))):
			return True
		if (t == hxunicode):
			return python_lib_Builtin.isinstance(v,String)
		isEnumType = (t == Enum)
		if ((isEnumType and python_lib_Inspect.isclass(v)) and python_lib_Builtin.hasattr(v,"_hx_constructs")):
			return True
		if isEnumType:
			return False
		isClassType = (t == Class)
		if ((((isClassType and (not python_lib_Builtin.isinstance(v,Enum))) and python_lib_Inspect.isclass(v)) and python_lib_Builtin.hasattr(v,"_hx_class_name")) and (not python_lib_Builtin.hasattr(v,"_hx_constructs"))):
			return True
		if isClassType:
			return False
		def _hx_local_6():
			_hx_local_5 = None
			try:
				_hx_local_5 = python_lib_Builtin.isinstance(v,t)
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e1 = _hx_e1
				_hx_local_5 = False
			return _hx_local_5
		if _hx_local_6():
			return True
		if python_lib_Inspect.isclass(t):
			loop = None
			loop1 = None
			def _hx_local_8(intf):
				f1 = None
				if python_lib_Builtin.hasattr(intf,"_hx_interfaces"):
					f1 = intf._hx_interfaces
				else:
					f1 = []
				if (f1 is not None):
					_g = 0
					while ((_g < python_lib_Builtin.len(f1))):
						i = (f1[_g] if _g >= 0 and _g < python_lib_Builtin.len(f1) else None)
						_g = (_g + 1)
						if HxOverrides.eq(i,t):
							return True
						else:
							l = loop1(i)
							if l:
								return True
					return False
				else:
					return False
			loop1 = _hx_local_8
			loop = loop1
			currentClass = v.__class__
			while ((currentClass is not None)):
				if loop(currentClass):
					return True
				currentClass = python_Boot.getSuperClass(currentClass)
			return False
		else:
			return False

	@staticmethod
	def string(s):
		return python_Boot.toString1(s,"")

	@staticmethod
	def parseInt(x):
		if (x is None):
			return None
		try:
			return python_lib_Builtin.int(x)
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e = _hx_e1
			try:
				prefix = None
				_this = HxString.substr(x,0,2)
				prefix = _this.lower()
				if (prefix == "0x"):
					return python_lib_Builtin.int(x,16)
				raise _HxException("fail")
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				e1 = _hx_e1
				r = None
				x1 = Std.parseFloat(x)
				try:
					r = python_lib_Builtin.int(x1)
				except Exception as _hx_e:
					_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
					e2 = _hx_e1
					r = None
				if (r is None):
					r1 = Std.shortenPossibleNumber(x)
					if (r1 != x):
						return Std.parseInt(r1)
					else:
						return None
				return r

	@staticmethod
	def shortenPossibleNumber(x):
		r = ""
		_g1 = 0
		_g = python_lib_Builtin.len(x)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			c = None
			if ((i < 0) or ((i >= python_lib_Builtin.len(x)))):
				c = ""
			else:
				c = x[i]
			_g2 = HxString.charCodeAt(c,0)
			if (_g2 is not None):
				if ((((((((((((_g2) == 46) or (((_g2) == 57))) or (((_g2) == 56))) or (((_g2) == 55))) or (((_g2) == 54))) or (((_g2) == 53))) or (((_g2) == 52))) or (((_g2) == 51))) or (((_g2) == 50))) or (((_g2) == 49))) or (((_g2) == 48))):
					r = (HxOverrides.stringOrNull(r) + HxOverrides.stringOrNull(c))
				else:
					break
			else:
				break
		return r

	@staticmethod
	def parseFloat(x):
		try:
			return python_lib_Builtin.float(x)
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e = _hx_e1
			if (x is not None):
				r1 = Std.shortenPossibleNumber(x)
				if (r1 != x):
					return Std.parseFloat(r1)
			return Math.NaN


Std = _hx_classes.registerClass("Std", statics=["is","string","parseInt","shortenPossibleNumber","parseFloat"])(Std)

class Void(object):
	pass
Void = _hx_classes.registerAbstract("Void")(Void)

class Float(object):
	pass
Float = _hx_classes.registerAbstract("Float")(Float)

class Int(object):
	pass
Int = _hx_classes.registerAbstract("Int")(Int)

class Bool(object):
	pass
Bool = _hx_classes.registerAbstract("Bool")(Bool)

class Dynamic(object):
	pass
Dynamic = _hx_classes.registerAbstract("Dynamic")(Dynamic)

class StringBuf(object):

	def __init__(self):
		self.b = None
		self.b = python_lib_io_StringIO()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.b = None
		_hx_o.length = None


StringBuf = _hx_classes.registerClass("StringBuf", fields=["b"])(StringBuf)

class StringTools(object):

	@staticmethod
	def isSpace(s,pos):
		if (((python_lib_Builtin.len(s) == 0) or ((pos < 0))) or ((pos >= python_lib_Builtin.len(s)))):
			return False
		c = HxString.charCodeAt(s,pos)
		return (((c > 8) and ((c < 14))) or ((c == 32)))

	@staticmethod
	def ltrim(s):
		l = python_lib_Builtin.len(s)
		r = 0
		while (((r < l) and StringTools.isSpace(s,r))):
			r = (r + 1)
		if (r > 0):
			return HxString.substr(s,r,(l - r))
		else:
			return s

	@staticmethod
	def rtrim(s):
		l = python_lib_Builtin.len(s)
		r = 0
		while (((r < l) and StringTools.isSpace(s,((l - r) - 1)))):
			r = (r + 1)
		if (r > 0):
			return HxString.substr(s,0,(l - r))
		else:
			return s

	@staticmethod
	def trim(s):
		return StringTools.ltrim(StringTools.rtrim(s))

	@staticmethod
	def lpad(s,c,l):
		if (python_lib_Builtin.len(c) <= 0):
			return s
		while ((python_lib_Builtin.len(s) < l)):
			s = (HxOverrides.stringOrNull(c) + HxOverrides.stringOrNull(s))
		return s

	@staticmethod
	def replace(s,sub,by):
		_this = None
		if (sub == ""):
			_this = python_lib_Builtin.list(s)
		else:
			_this = s.split(sub)
		return by.join([python_Boot.toString1(x1,'') for x1 in _this])


StringTools = _hx_classes.registerClass("StringTools", statics=["isSpace","ltrim","rtrim","trim","lpad","replace"])(StringTools)

class haxe_IMap(object):
	pass
haxe_IMap = _hx_classes.registerClass("haxe.IMap", methods=["get"])(haxe_IMap)

class haxe_ds_StringMap(object):

	def __init__(self):
		self.h = None
		self.h = python_lib_Dict()

	def get(self,key):
		return self.h.get(key,None)

	def keys(self):
		this1 = None
		_this = self.h.keys()
		this1 = python_lib_Builtin.iter(_this)
		return python_HaxeIterator(this1)

	def iterator(self):
		this1 = None
		_this = self.h.values()
		this1 = python_lib_Builtin.iter(_this)
		return python_HaxeIterator(this1)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None


haxe_ds_StringMap = _hx_classes.registerClass("haxe.ds.StringMap", fields=["h"], methods=["get","keys","iterator"], interfaces=[haxe_IMap])(haxe_ds_StringMap)

class python_HaxeIterator(object):

	def __init__(self,it):
		self.it = None
		self.x = None
		self.has = None
		self.checked = None
		self.checked = False
		self.has = False
		self.x = None
		self.it = it

	def __next__(self): return self.next()

	def next(self):
		if (not self.checked):
			self.hasNext()
		self.checked = False
		return self.x

	def hasNext(self):
		if (not self.checked):
			try:
				self.x = hxnext(self.it)
				self.has = True
			except Exception as _hx_e:
				_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
				if python_lib_Builtin.isinstance(_hx_e1, StopIteration):
					s = _hx_e1
					self.has = False
					self.x = None
				else:
					raise _hx_e
			self.checked = True
		return self.has

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.it = None
		_hx_o.x = None
		_hx_o.has = None
		_hx_o.checked = None


python_HaxeIterator = _hx_classes.registerClass("python.HaxeIterator", fields=["it","x","has","checked"], methods=["next","hasNext"])(python_HaxeIterator)

class Sys(object):

	@staticmethod
	def args():
		argv = python_lib_Sys.argv
		return argv[1:None]

	@staticmethod
	def getEnv(s):
		return Sys.environ.h.get(s,None)

	@staticmethod
	def command(cmd,args = None):
		args1 = None
		if (args is None):
			args1 = [cmd]
		else:
			args1 = ([cmd] + args)
		return python_lib_Subprocess.call(args1)

	@staticmethod
	def stdout():
		return python_io_IoTools.createFileOutputFromText(python_lib_Sys.stdout)

	@staticmethod
	def stderr():
		return python_io_IoTools.createFileOutputFromText(python_lib_Sys.stderr)


Sys = _hx_classes.registerClass("Sys", statics=["environ","args","getEnv","command","stdout","stderr"])(Sys)

class TableComparisonState(object):

	def __init__(self):
		self.p = None
		self.a = None
		self.b = None
		self.completed = None
		self.run_to_completion = None
		self.is_equal = None
		self.is_equal_known = None
		self.has_same_columns = None
		self.has_same_columns_known = None
		self.compare_flags = None
		self.p_meta = None
		self.a_meta = None
		self.b_meta = None
		self.alignment = None
		self.children = None
		self.child_order = None
		self.reset()

	def reset(self):
		self.completed = False
		self.run_to_completion = True
		self.is_equal_known = False
		self.is_equal = False
		self.has_same_columns = False
		self.has_same_columns_known = False
		self.compare_flags = None
		self.alignment = None
		self.children = None
		self.child_order = None

	def getMeta(self):
		if ((self.p is not None) and ((self.p_meta is None))):
			self.p_meta = self.p.getMeta()
		if ((self.a is not None) and ((self.a_meta is None))):
			self.a_meta = self.a.getMeta()
		if ((self.b is not None) and ((self.b_meta is None))):
			self.b_meta = self.b.getMeta()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.p = None
		_hx_o.a = None
		_hx_o.b = None
		_hx_o.completed = None
		_hx_o.run_to_completion = None
		_hx_o.is_equal = None
		_hx_o.is_equal_known = None
		_hx_o.has_same_columns = None
		_hx_o.has_same_columns_known = None
		_hx_o.compare_flags = None
		_hx_o.p_meta = None
		_hx_o.a_meta = None
		_hx_o.b_meta = None
		_hx_o.alignment = None
		_hx_o.children = None
		_hx_o.child_order = None


TableComparisonState = _hx_classes.registerClass("TableComparisonState", fields=["p","a","b","completed","run_to_completion","is_equal","is_equal_known","has_same_columns","has_same_columns_known","compare_flags","p_meta","a_meta","b_meta","alignment","children","child_order"], methods=["reset","getMeta"])(TableComparisonState)

class TableDiff(object):

	def __init__(self,align,flags):
		self.align = None
		self.flags = None
		self.builder = None
		self.row_map = None
		self.col_map = None
		self.has_parent = None
		self.a = None
		self.b = None
		self.p = None
		self.rp_header = None
		self.ra_header = None
		self.rb_header = None
		self.is_index_p = None
		self.is_index_a = None
		self.is_index_b = None
		self.order = None
		self.row_units = None
		self.column_units = None
		self.show_rc_numbers = None
		self.row_moves = None
		self.col_moves = None
		self.active_row = None
		self.active_column = None
		self.allow_insert = None
		self.allow_delete = None
		self.allow_update = None
		self.v = None
		self.sep = None
		self.conflict_sep = None
		self.schema = None
		self.have_schema = None
		self.top_line_done = None
		self.have_addition = None
		self.act = None
		self.publish = None
		self.diff_found = None
		self.schema_diff_found = None
		self.preserve_columns = None
		self.nested = None
		self.nesting_present = None
		self.align = align
		self.flags = flags
		self.builder = None
		self.preserve_columns = False

	def setCellBuilder(self,builder):
		self.builder = builder

	def getSeparator(self,t,t2,root):
		sep = root
		w = t.get_width()
		h = t.get_height()
		view = t.getCellView()
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				txt = view.toString(t.getCell(x,y))
				if (txt is None):
					continue
				while ((txt.find(sep) >= 0)):
					sep = ("-" + HxOverrides.stringOrNull(sep))
		if (t2 is not None):
			w = t2.get_width()
			h = t2.get_height()
			_g2 = 0
			while ((_g2 < h)):
				y1 = _g2
				_g2 = (_g2 + 1)
				_g11 = 0
				while ((_g11 < w)):
					x1 = _g11
					_g11 = (_g11 + 1)
					txt1 = view.toString(t2.getCell(x1,y1))
					if (txt1 is None):
						continue
					while ((txt1.find(sep) >= 0)):
						sep = ("-" + HxOverrides.stringOrNull(sep))
		return sep

	def quoteForDiff(self,v,d):
		nil = "NULL"
		if v.equals(d,None):
			return nil
		unicode = v.toString(d)
		score = 0
		_g1 = 0
		_g = python_lib_Builtin.len(unicode)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (HxString.charCodeAt(unicode,score) != 95):
				break
			score = (score + 1)
		if (HxString.substr(unicode,score,None) == nil):
			unicode = ("_" + HxOverrides.stringOrNull(unicode))
		return unicode

	def isReordered(self,m,ct):
		reordered = False
		l = -1
		r = -1
		_g = 0
		while ((_g < ct)):
			i = _g
			_g = (_g + 1)
			unit = m.h.get(i,None)
			if (unit is None):
				continue
			if (unit.l >= 0):
				if (unit.l < l):
					reordered = True
					break
				l = unit.l
			if (unit.r >= 0):
				if (unit.r < r):
					reordered = True
					break
				r = unit.r
		return reordered

	def spreadContext(self,units,_hx_del,active):
		if ((_hx_del > 0) and ((active is not None))):
			mark = (-_hx_del - 1)
			skips = 0
			_g1 = 0
			_g = python_lib_Builtin.len(units)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				if ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == -3):
					skips = (skips + 1)
					continue
				if (((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 0) or (((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 3))):
					if ((i - mark) <= ((_hx_del + skips))):
						python_internal_ArrayImpl._set(active, i, 2)
					elif ((i - mark) == (((_hx_del + 1) + skips))):
						python_internal_ArrayImpl._set(active, i, 3)
				elif ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 1):
					mark = i
					skips = 0
			mark = ((python_lib_Builtin.len(units) + _hx_del) + 1)
			skips = 0
			_g11 = 0
			_g2 = python_lib_Builtin.len(units)
			while ((_g11 < _g2)):
				j = _g11
				_g11 = (_g11 + 1)
				i1 = ((python_lib_Builtin.len(units) - 1) - j)
				if ((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == -3):
					skips = (skips + 1)
					continue
				if (((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == 0) or (((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == 3))):
					if ((mark - i1) <= ((_hx_del + skips))):
						python_internal_ArrayImpl._set(active, i1, 2)
					elif ((mark - i1) == (((_hx_del + 1) + skips))):
						python_internal_ArrayImpl._set(active, i1, 3)
				elif ((active[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(active) else None) == 1):
					mark = i1
					skips = 0

	def setIgnore(self,ignore,idx_ignore,tab,r_header):
		v = tab.getCellView()
		if (tab.get_height() >= r_header):
			_g1 = 0
			_g = tab.get_width()
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				name = v.toString(tab.getCell(i,r_header))
				if (not name in ignore.h):
					continue
				idx_ignore.set(i,True)

	def countActive(self,active):
		ct = 0
		showed_dummy = False
		_g1 = 0
		_g = python_lib_Builtin.len(active)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			publish = ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) > 0)
			dummy = ((active[i] if i >= 0 and i < python_lib_Builtin.len(active) else None) == 3)
			if (dummy and showed_dummy):
				continue
			if (not publish):
				continue
			showed_dummy = dummy
			ct = (ct + 1)
		return ct

	def reset(self):
		self.has_parent = False
		def _hx_local_1():
			def _hx_local_0():
				self.rb_header = 0
				return self.rb_header
			self.ra_header = _hx_local_0()
			return self.ra_header
		self.rp_header = _hx_local_1()
		self.is_index_p = haxe_ds_IntMap()
		self.is_index_a = haxe_ds_IntMap()
		self.is_index_b = haxe_ds_IntMap()
		self.row_map = haxe_ds_IntMap()
		self.col_map = haxe_ds_IntMap()
		self.show_rc_numbers = False
		self.row_moves = None
		self.col_moves = None
		def _hx_local_3():
			def _hx_local_2():
				self.allow_update = True
				return self.allow_update
			self.allow_delete = _hx_local_2()
			return self.allow_delete
		self.allow_insert = _hx_local_3()
		self.sep = ""
		self.conflict_sep = ""
		self.top_line_done = False
		self.diff_found = False
		self.schema_diff_found = False

	def setupTables(self):
		self.order = self.align.toOrder()
		self.row_units = self.order.getList()
		self.has_parent = (self.align.reference is not None)
		if self.has_parent:
			self.p = self.align.getSource()
			self.a = self.align.reference.getTarget()
			self.b = self.align.getTarget()
			self.rp_header = self.align.reference.meta.getSourceHeader()
			self.ra_header = self.align.reference.meta.getTargetHeader()
			self.rb_header = self.align.meta.getTargetHeader()
			if (self.align.getIndexColumns() is not None):
				_g = 0
				_g1 = self.align.getIndexColumns()
				while ((_g < python_lib_Builtin.len(_g1))):
					p2b = (_g1[_g] if _g >= 0 and _g < python_lib_Builtin.len(_g1) else None)
					_g = (_g + 1)
					if (p2b.l >= 0):
						self.is_index_p.set(p2b.l,True)
					if (p2b.r >= 0):
						self.is_index_b.set(p2b.r,True)
			if (self.align.reference.getIndexColumns() is not None):
				_g2 = 0
				_g11 = self.align.reference.getIndexColumns()
				while ((_g2 < python_lib_Builtin.len(_g11))):
					p2a = (_g11[_g2] if _g2 >= 0 and _g2 < python_lib_Builtin.len(_g11) else None)
					_g2 = (_g2 + 1)
					if (p2a.l >= 0):
						self.is_index_p.set(p2a.l,True)
					if (p2a.r >= 0):
						self.is_index_a.set(p2a.r,True)
		else:
			self.a = self.align.getSource()
			self.b = self.align.getTarget()
			self.p = self.a
			self.ra_header = self.align.meta.getSourceHeader()
			self.rp_header = self.ra_header
			self.rb_header = self.align.meta.getTargetHeader()
			if (self.align.getIndexColumns() is not None):
				_g3 = 0
				_g12 = self.align.getIndexColumns()
				while ((_g3 < python_lib_Builtin.len(_g12))):
					a2b = (_g12[_g3] if _g3 >= 0 and _g3 < python_lib_Builtin.len(_g12) else None)
					_g3 = (_g3 + 1)
					if (a2b.l >= 0):
						self.is_index_a.set(a2b.l,True)
					if (a2b.r >= 0):
						self.is_index_b.set(a2b.r,True)
		self.allow_insert = self.flags.allowInsert()
		self.allow_delete = self.flags.allowDelete()
		self.allow_update = self.flags.allowUpdate()
		common = self.a
		if (common is None):
			common = self.b
		if (common is None):
			common = self.p
		self.v = common.getCellView()
		self.builder.setView(self.v)
		self.nested = False
		meta = common.getMeta()
		if (meta is not None):
			self.nested = meta.isNested()
		self.nesting_present = False

	def scanActivity(self):
		self.active_row = list()
		self.active_column = None
		if (not self.flags.show_unchanged):
			_g1 = 0
			_g = python_lib_Builtin.len(self.row_units)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				python_internal_ArrayImpl._set(self.active_row, ((python_lib_Builtin.len(self.row_units) - 1) - i), 0)
		if (not self.flags.show_unchanged_columns):
			self.active_column = list()
			_g11 = 0
			_g2 = python_lib_Builtin.len(self.column_units)
			while ((_g11 < _g2)):
				i1 = _g11
				_g11 = (_g11 + 1)
				v = 0
				unit = (self.column_units[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(self.column_units) else None)
				if ((unit.l >= 0) and self.is_index_a.h.get(unit.l,None)):
					v = 1
				if ((unit.r >= 0) and self.is_index_b.h.get(unit.r,None)):
					v = 1
				if ((unit.p >= 0) and self.is_index_p.h.get(unit.p,None)):
					v = 1
				python_internal_ArrayImpl._set(self.active_column, i1, v)

	def setupColumns(self):
		column_order = self.align.meta.toOrder()
		self.column_units = column_order.getList()
		ignore = self.flags.getIgnoredColumns()
		if (ignore is not None):
			p_ignore = haxe_ds_IntMap()
			a_ignore = haxe_ds_IntMap()
			b_ignore = haxe_ds_IntMap()
			self.setIgnore(ignore,p_ignore,self.p,self.rp_header)
			self.setIgnore(ignore,a_ignore,self.a,self.ra_header)
			self.setIgnore(ignore,b_ignore,self.b,self.rb_header)
			ncolumn_units = list()
			_g1 = 0
			_g = python_lib_Builtin.len(self.column_units)
			while ((_g1 < _g)):
				j = _g1
				_g1 = (_g1 + 1)
				cunit = (self.column_units[j] if j >= 0 and j < python_lib_Builtin.len(self.column_units) else None)
				if ((cunit.p in p_ignore.h or cunit.l in a_ignore.h) or cunit.r in b_ignore.h):
					continue
				ncolumn_units.append(cunit)
				python_lib_Builtin.len(ncolumn_units)
			self.column_units = ncolumn_units

	def setupMoves(self):
		if self.flags.ordered:
			self.row_moves = haxe_ds_IntMap()
			moves = Mover.moveUnits(self.row_units)
			_g1 = 0
			_g = python_lib_Builtin.len(moves)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				self.row_moves.set((moves[i] if i >= 0 and i < python_lib_Builtin.len(moves) else None),i)
				i
			self.col_moves = haxe_ds_IntMap()
			moves = Mover.moveUnits(self.column_units)
			_g11 = 0
			_g2 = python_lib_Builtin.len(moves)
			while ((_g11 < _g2)):
				i1 = _g11
				_g11 = (_g11 + 1)
				self.col_moves.set((moves[i1] if i1 >= 0 and i1 < python_lib_Builtin.len(moves) else None),i1)
				i1

	def scanSchema(self):
		self.schema = list()
		self.have_schema = False
		_g1 = 0
		_g = python_lib_Builtin.len(self.column_units)
		while ((_g1 < _g)):
			j = _g1
			_g1 = (_g1 + 1)
			cunit = (self.column_units[j] if j >= 0 and j < python_lib_Builtin.len(self.column_units) else None)
			reordered = False
			if self.flags.ordered:
				if j in self.col_moves.h:
					reordered = True
				if reordered:
					self.show_rc_numbers = True
			act = ""
			if ((cunit.r >= 0) and ((cunit.lp() == -1))):
				self.have_schema = True
				act = "+++"
				if (self.active_column is not None):
					if self.allow_update:
						python_internal_ArrayImpl._set(self.active_column, j, 1)
			if ((cunit.r < 0) and ((cunit.lp() >= 0))):
				self.have_schema = True
				act = "---"
				if (self.active_column is not None):
					if self.allow_update:
						python_internal_ArrayImpl._set(self.active_column, j, 1)
			if ((cunit.r >= 0) and ((cunit.lp() >= 0))):
				if ((self.p.get_height() >= self.rp_header) and ((self.b.get_height() >= self.rb_header))):
					pp = self.p.getCell(cunit.lp(),self.rp_header)
					bb = self.b.getCell(cunit.r,self.rb_header)
					if (not self.isEqual(self.v,pp,bb)):
						self.have_schema = True
						act = "("
						act = (HxOverrides.stringOrNull(act) + HxOverrides.stringOrNull(self.v.toString(pp)))
						act = (HxOverrides.stringOrNull(act) + ")")
						if (self.active_column is not None):
							python_internal_ArrayImpl._set(self.active_column, j, 1)
			if reordered:
				act = (":" + HxOverrides.stringOrNull(act))
				self.have_schema = True
				if (self.active_column is not None):
					self.active_column = None
			_this = self.schema
			_this.append(act)
			python_lib_Builtin.len(_this)

	def checkRcNumbers(self,w,h):
		if (not self.show_rc_numbers):
			if self.flags.always_show_order:
				self.show_rc_numbers = True
			elif self.flags.ordered:
				self.show_rc_numbers = self.isReordered(self.row_map,h)
				if (not self.show_rc_numbers):
					self.show_rc_numbers = self.isReordered(self.col_map,w)

	def addRcNumbers(self,output):
		admin_w = 1
		if (self.show_rc_numbers and (not self.flags.never_show_order)):
			admin_w = (admin_w + 1)
			target = list()
			_g1 = 0
			_g = output.get_width()
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				target.append((i + 1))
				python_lib_Builtin.len(target)
			output.insertOrDeleteColumns(target,(output.get_width() + 1))
			_g11 = 0
			_g2 = output.get_height()
			while ((_g11 < _g2)):
				i1 = _g11
				_g11 = (_g11 + 1)
				unit = self.row_map.h.get(i1,None)
				if (unit is None):
					output.setCell(0,i1,"")
					continue
				output.setCell(0,i1,self.builder.links(unit,True))
			target = list()
			_g12 = 0
			_g3 = output.get_height()
			while ((_g12 < _g3)):
				i2 = _g12
				_g12 = (_g12 + 1)
				target.append((i2 + 1))
				python_lib_Builtin.len(target)
			output.insertOrDeleteRows(target,(output.get_height() + 1))
			_g13 = 1
			_g4 = output.get_width()
			while ((_g13 < _g4)):
				i3 = _g13
				_g13 = (_g13 + 1)
				unit1 = self.col_map.h.get((i3 - 1),None)
				if (unit1 is None):
					output.setCell(i3,0,"")
					continue
				output.setCell(i3,0,self.builder.links(unit1,False))
			output.setCell(0,0,self.builder.marker("@:@"))
		return admin_w

	def elideColumns(self,output,admin_w):
		if (self.active_column is not None):
			all_active = True
			_g1 = 0
			_g = python_lib_Builtin.len(self.active_column)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				if ((self.active_column[i] if i >= 0 and i < python_lib_Builtin.len(self.active_column) else None) == 0):
					all_active = False
					break
			if (not all_active):
				fate = list()
				_g2 = 0
				while ((_g2 < admin_w)):
					i1 = _g2
					_g2 = (_g2 + 1)
					fate.append(i1)
					python_lib_Builtin.len(fate)
				at = admin_w
				ct = 0
				dots = list()
				_g11 = 0
				_g3 = python_lib_Builtin.len(self.active_column)
				while ((_g11 < _g3)):
					i2 = _g11
					_g11 = (_g11 + 1)
					off = ((self.active_column[i2] if i2 >= 0 and i2 < python_lib_Builtin.len(self.active_column) else None) == 0)
					if off:
						ct = (ct + 1)
					else:
						ct = 0
					if (off and ((ct > 1))):
						fate.append(-1)
						python_lib_Builtin.len(fate)
					else:
						if off:
							dots.append(at)
							python_lib_Builtin.len(dots)
						fate.append(at)
						python_lib_Builtin.len(fate)
						at = (at + 1)
				output.insertOrDeleteColumns(fate,at)
				_g4 = 0
				while ((_g4 < python_lib_Builtin.len(dots))):
					d = (dots[_g4] if _g4 >= 0 and _g4 < python_lib_Builtin.len(dots) else None)
					_g4 = (_g4 + 1)
					_g21 = 0
					_g12 = output.get_height()
					while ((_g21 < _g12)):
						j = _g21
						_g21 = (_g21 + 1)
						output.setCell(d,j,self.builder.marker("..."))

	def addSchema(self,output):
		if self.have_schema:
			at = output.get_height()
			output.resize((python_lib_Builtin.len(self.column_units) + 1),(at + 1))
			output.setCell(0,at,self.builder.marker("!"))
			_g1 = 0
			_g = python_lib_Builtin.len(self.column_units)
			while ((_g1 < _g)):
				j = _g1
				_g1 = (_g1 + 1)
				output.setCell((j + 1),at,self.v.toDatum((self.schema[j] if j >= 0 and j < python_lib_Builtin.len(self.schema) else None)))
			self.schema_diff_found = True

	def addHeader(self,output):
		if self.flags.always_show_header:
			at = output.get_height()
			output.resize((python_lib_Builtin.len(self.column_units) + 1),(at + 1))
			output.setCell(0,at,self.builder.marker("@@"))
			_g1 = 0
			_g = python_lib_Builtin.len(self.column_units)
			while ((_g1 < _g)):
				j = _g1
				_g1 = (_g1 + 1)
				cunit = (self.column_units[j] if j >= 0 and j < python_lib_Builtin.len(self.column_units) else None)
				if (cunit.r >= 0):
					if (self.b.get_height() != 0):
						output.setCell((j + 1),at,self.b.getCell(cunit.r,self.rb_header))
				elif (cunit.l >= 0):
					if (self.a.get_height() != 0):
						output.setCell((j + 1),at,self.a.getCell(cunit.l,self.ra_header))
				elif (cunit.lp() >= 0):
					if (self.p.get_height() != 0):
						output.setCell((j + 1),at,self.p.getCell(cunit.lp(),self.rp_header))
				self.col_map.set((j + 1),cunit)
			self.top_line_done = True

	def checkMeta(self,t,meta):
		if (meta.get_width() != ((t.get_width() + 1))):
			return False
		if ((meta.get_width() == 0) or ((meta.get_height() == 0))):
			return False
		return True

	def getMetaTable(self,t):
		if (t is None):
			return None
		meta = t.getMeta()
		if (meta is None):
			return None
		return meta.asTable()

	def addMeta(self,output):
		a_meta = None
		b_meta = None
		p_meta = None
		a_meta = self.getMetaTable(self.a)
		b_meta = self.getMetaTable(self.b)
		p_meta = self.getMetaTable(self.p)
		if (((a_meta is None) or ((b_meta is None))) or ((p_meta is None))):
			return False
		if (not self.checkMeta(self.a,a_meta)):
			return False
		if (not self.checkMeta(self.b,b_meta)):
			return False
		if (not self.checkMeta(self.p,p_meta)):
			return False
		if (not self.flags.show_meta):
			return False
		meta_diff = SimpleTable(0, 0)
		meta_flags = CompareFlags()
		meta_flags.addPrimaryKey("@@")
		meta_flags.addPrimaryKey("@")
		meta_flags.unchanged_column_context = 65536
		meta_flags.unchanged_context = 0
		meta_align = Coopy.compareTables3((None if ((a_meta == p_meta)) else p_meta),a_meta,b_meta,meta_flags).align()
		td = TableDiff(meta_align, meta_flags)
		td.preserve_columns = True
		td.hilite(meta_diff)
		if td.hasDifference():
			h = output.get_height()
			dh = meta_diff.get_height()
			offset = None
			if td.hasSchemaDifference():
				offset = 2
			else:
				offset = 1
			output.resize(output.get_width(),((h + dh) - offset))
			v = meta_diff.getCellView()
			_g = offset
			while ((_g < dh)):
				y = _g
				_g = (_g + 1)
				_g2 = 1
				_g1 = meta_diff.get_width()
				while ((_g2 < _g1)):
					x = _g2
					_g2 = (_g2 + 1)
					c = meta_diff.getCell(x,y)
					if (x == 1):
						c = ((("@" + HxOverrides.stringOrNull(v.toString(c))) + "@") + HxOverrides.stringOrNull(v.toString(meta_diff.getCell(0,y))))
					output.setCell((x - 1),((h + y) - offset),c)
			if (self.active_column is not None):
				if (python_lib_Builtin.len(td.active_column) == meta_diff.get_width()):
					_g11 = 1
					_g3 = meta_diff.get_width()
					while ((_g11 < _g3)):
						i = _g11
						_g11 = (_g11 + 1)
						if ((td.active_column[i] if i >= 0 and i < python_lib_Builtin.len(td.active_column) else None) >= 0):
							python_internal_ArrayImpl._set(self.active_column, (i - 1), 1)
		return False

	def refineActivity(self):
		self.spreadContext(self.row_units,self.flags.unchanged_context,self.active_row)
		self.spreadContext(self.column_units,self.flags.unchanged_column_context,self.active_column)
		if (self.active_column is not None):
			_g1 = 0
			_g = python_lib_Builtin.len(self.column_units)
			while ((_g1 < _g)):
				i = _g1
				_g1 = (_g1 + 1)
				if ((self.active_column[i] if i >= 0 and i < python_lib_Builtin.len(self.active_column) else None) == 3):
					python_internal_ArrayImpl._set(self.active_column, i, 0)

	def normalizeString(self,v,unicode):
		if (unicode is None):
			return unicode
		if (not ((self.flags.ignore_whitespace or self.flags.ignore_case))):
			return unicode
		txt = v.toString(unicode)
		if self.flags.ignore_whitespace:
			txt = StringTools.trim(txt)
		if self.flags.ignore_case:
			txt = txt.lower()
		return txt

	def isEqual(self,v,aa,bb):
		if (self.flags.ignore_whitespace or self.flags.ignore_case):
			return (self.normalizeString(v,aa) == self.normalizeString(v,bb))
		return v.equals(aa,bb)

	def checkNesting(self,v,have_ll,ll,have_rr,rr,have_pp,pp,x,y):
		all_tables = True
		if have_ll:
			all_tables = (all_tables and v.isTable(ll))
		if have_rr:
			all_tables = (all_tables and v.isTable(rr))
		if have_pp:
			all_tables = (all_tables and v.isTable(pp))
		if (not all_tables):
			return [ll, rr, pp]
		ll_table = None
		rr_table = None
		pp_table = None
		if have_ll:
			ll_table = v.getTable(ll)
		if have_rr:
			rr_table = v.getTable(rr)
		if have_pp:
			pp_table = v.getTable(pp)
		compare = False
		comp = TableComparisonState()
		comp.a = ll_table
		comp.b = rr_table
		comp.p = pp_table
		comp.compare_flags = self.flags
		comp.getMeta()
		key = None
		if (comp.a_meta is not None):
			key = comp.a_meta.getName()
		if ((key is None) and ((comp.b_meta is not None))):
			key = comp.b_meta.getName()
		if (key is None):
			key = ((Std.string(x) + "_") + Std.string(y))
		if (self.align.comp is not None):
			if (self.align.comp.children is None):
				self.align.comp.children = haxe_ds_StringMap()
				self.align.comp.child_order = list()
				compare = True
			else:
				compare = (not key in self.align.comp.children.h)
		if compare:
			self.nesting_present = True
			self.align.comp.children.h[key] = comp
			_this = self.align.comp.child_order
			_this.append(key)
			python_lib_Builtin.len(_this)
			ct = CompareTable(comp)
			ct.align()
		else:
			comp = self.align.comp.children.h.get(key,None)
		ll_out = None
		rr_out = None
		pp_out = None
		if ((comp.alignment.isMarkedAsIdentical() or ((have_ll and (not have_rr)))) or ((have_rr and (not have_ll)))):
			ll_out = (("[" + HxOverrides.stringOrNull(key)) + "]")
			rr_out = ll_out
			pp_out = ll_out
		else:
			if (ll is not None):
				ll_out = (("[a." + HxOverrides.stringOrNull(key)) + "]")
			if (rr is not None):
				rr_out = (("[b." + HxOverrides.stringOrNull(key)) + "]")
			if (pp is not None):
				pp_out = (("[p." + HxOverrides.stringOrNull(key)) + "]")
		return [ll_out, rr_out, pp_out]

	def scanRow(self,unit,output,at,i):
		_g1 = 0
		_g = python_lib_Builtin.len(self.column_units)
		while ((_g1 < _g)):
			j = _g1
			_g1 = (_g1 + 1)
			cunit = (self.column_units[j] if j >= 0 and j < python_lib_Builtin.len(self.column_units) else None)
			pp = None
			ll = None
			rr = None
			dd = None
			dd_to = None
			have_dd_to = False
			dd_to_alt = None
			have_dd_to_alt = False
			have_pp = False
			have_ll = False
			have_rr = False
			if ((cunit.p >= 0) and ((unit.p >= 0))):
				pp = self.p.getCell(cunit.p,unit.p)
				have_pp = True
			if ((cunit.l >= 0) and ((unit.l >= 0))):
				ll = self.a.getCell(cunit.l,unit.l)
				have_ll = True
			if ((cunit.r >= 0) and ((unit.r >= 0))):
				rr = self.b.getCell(cunit.r,unit.r)
				have_rr = True
				if (((cunit.p if (have_pp) else cunit.l)) < 0):
					if (rr is not None):
						if (self.v.toString(rr) != ""):
							if self.flags.allowUpdate():
								self.have_addition = True
			if self.nested:
				ndiff = self.checkNesting(self.v,have_ll,ll,have_rr,rr,have_pp,pp,i,j)
				ll = (ndiff[0] if 0 < python_lib_Builtin.len(ndiff) else None)
				rr = (ndiff[1] if 1 < python_lib_Builtin.len(ndiff) else None)
				pp = (ndiff[2] if 2 < python_lib_Builtin.len(ndiff) else None)
			if have_pp:
				if (not have_rr):
					dd = pp
				elif self.isEqual(self.v,pp,rr):
					dd = ll
				else:
					dd = pp
					dd_to = rr
					have_dd_to = True
					if (not self.isEqual(self.v,pp,ll)):
						if (not self.isEqual(self.v,pp,rr)):
							dd_to_alt = ll
							have_dd_to_alt = True
			elif have_ll:
				if (not have_rr):
					dd = ll
				elif self.isEqual(self.v,ll,rr):
					dd = ll
				else:
					dd = ll
					dd_to = rr
					have_dd_to = True
			else:
				dd = rr
			cell = dd
			if (have_dd_to and self.allow_update):
				if (self.active_column is not None):
					python_internal_ArrayImpl._set(self.active_column, j, 1)
				if (self.sep == ""):
					if self.builder.needSeparator():
						self.sep = self.getSeparator(self.a,self.b,"->")
						self.builder.setSeparator(self.sep)
					else:
						self.sep = "->"
				is_conflict = False
				if have_dd_to_alt:
					if (not self.isEqual(self.v,dd_to,dd_to_alt)):
						is_conflict = True
				if (not is_conflict):
					cell = self.builder.update(dd,dd_to)
					if (python_lib_Builtin.len(self.sep) > python_lib_Builtin.len(self.act)):
						self.act = self.sep
				else:
					if (self.conflict_sep == ""):
						if self.builder.needSeparator():
							self.conflict_sep = (HxOverrides.stringOrNull(self.getSeparator(self.p,self.a,"!")) + HxOverrides.stringOrNull(self.sep))
							self.builder.setConflictSeparator(self.conflict_sep)
						else:
							self.conflict_sep = "!->"
					cell = self.builder.conflict(dd,dd_to_alt,dd_to)
					self.act = self.conflict_sep
			if ((self.act == "") and self.have_addition):
				self.act = "+"
			if (self.act == "+++"):
				if have_rr:
					if (self.active_column is not None):
						python_internal_ArrayImpl._set(self.active_column, j, 1)
			if self.publish:
				if ((self.active_column is None) or (((self.active_column[j] if j >= 0 and j < python_lib_Builtin.len(self.active_column) else None) > 0))):
					output.setCell((j + 1),at,cell)
		if self.publish:
			output.setCell(0,at,self.builder.marker(self.act))
			self.row_map.set(at,unit)
		if (self.act != ""):
			self.diff_found = True
			if (not self.publish):
				if (self.active_row is not None):
					python_internal_ArrayImpl._set(self.active_row, i, 1)

	def hilite(self,output):
		output = Coopy.tablify(output)
		return self.hiliteSingle(output)

	def hiliteSingle(self,output):
		if (not output.isResizable()):
			return False
		if (self.builder is None):
			if self.flags.allow_nested_cells:
				self.builder = NestedCellBuilder()
			else:
				self.builder = FlatCellBuilder(self.flags)
		output.resize(0,0)
		output.clear()
		self.reset()
		self.setupTables()
		self.setupColumns()
		self.setupMoves()
		self.scanActivity()
		self.scanSchema()
		self.addSchema(output)
		self.addHeader(output)
		self.addMeta(output)
		outer_reps_needed = None
		if (self.flags.show_unchanged and self.flags.show_unchanged_columns):
			outer_reps_needed = 1
		else:
			outer_reps_needed = 2
		output_height = output.get_height()
		output_height_init = output.get_height()
		_g = 0
		while ((_g < outer_reps_needed)):
			out = _g
			_g = (_g + 1)
			if (out == 1):
				self.refineActivity()
				rows = (self.countActive(self.active_row) + output_height_init)
				if self.top_line_done:
					rows = (rows - 1)
				output_height = output_height_init
				if (rows > output.get_height()):
					output.resize((python_lib_Builtin.len(self.column_units) + 1),rows)
			showed_dummy = False
			l = -1
			r = -1
			_g2 = 0
			_g1 = python_lib_Builtin.len(self.row_units)
			while ((_g2 < _g1)):
				i = _g2
				_g2 = (_g2 + 1)
				unit = (self.row_units[i] if i >= 0 and i < python_lib_Builtin.len(self.row_units) else None)
				reordered = False
				if self.flags.ordered:
					if i in self.row_moves.h:
						reordered = True
					if reordered:
						self.show_rc_numbers = True
				if ((unit.r < 0) and ((unit.l < 0))):
					continue
				if (((unit.r == 0) and ((unit.lp() <= 0))) and self.top_line_done):
					continue
				self.publish = self.flags.show_unchanged
				dummy = False
				if (out == 1):
					self.publish = ((self.active_row[i] if i >= 0 and i < python_lib_Builtin.len(self.active_row) else None) > 0)
					dummy = ((self.active_row[i] if i >= 0 and i < python_lib_Builtin.len(self.active_row) else None) == 3)
					if (dummy and showed_dummy):
						continue
					if (not self.publish):
						continue
				if (not dummy):
					showed_dummy = False
				at = output_height
				if self.publish:
					output_height = (output_height + 1)
					if (output.get_height() < output_height):
						output.resize((python_lib_Builtin.len(self.column_units) + 1),output_height)
				if dummy:
					_g4 = 0
					_g3 = (python_lib_Builtin.len(self.column_units) + 1)
					while ((_g4 < _g3)):
						j = _g4
						_g4 = (_g4 + 1)
						output.setCell(j,at,self.v.toDatum("..."))
					showed_dummy = True
					continue
				self.have_addition = False
				skip = False
				self.act = ""
				if reordered:
					self.act = ":"
				if (((unit.p < 0) and ((unit.l < 0))) and ((unit.r >= 0))):
					if (not self.allow_insert):
						skip = True
					self.act = "+++"
				if (((((unit.p >= 0) or (not self.has_parent))) and ((unit.l >= 0))) and ((unit.r < 0))):
					if (not self.allow_delete):
						skip = True
					self.act = "---"
				if skip:
					if (not self.publish):
						if (self.active_row is not None):
							python_internal_ArrayImpl._set(self.active_row, i, -3)
					continue
				self.scanRow(unit,output,at,i)
		self.checkRcNumbers(output.get_width(),output.get_height())
		admin_w = self.addRcNumbers(output)
		if (not self.preserve_columns):
			self.elideColumns(output,admin_w)
		return True

	def hiliteWithNesting(self,output):
		base = output.add("base")
		result = self.hiliteSingle(base)
		if (not result):
			return False
		if (self.align.comp is None):
			return True
		order = self.align.comp.child_order
		if (order is None):
			return True
		output.alignment = self.align
		_g = 0
		while ((_g < python_lib_Builtin.len(order))):
			name = (order[_g] if _g >= 0 and _g < python_lib_Builtin.len(order) else None)
			_g = (_g + 1)
			child = self.align.comp.children.h.get(name,None)
			alignment = child.alignment
			if alignment.isMarkedAsIdentical():
				self.align.comp.children.h[name] = None
				continue
			td = TableDiff(alignment, self.flags)
			child_output = output.add(name)
			result = (result and td.hiliteSingle(child_output))
		return result

	def hasDifference(self):
		return self.diff_found

	def hasSchemaDifference(self):
		return self.schema_diff_found

	def isNested(self):
		return self.nesting_present

	def getComparisonState(self):
		if (self.align is None):
			return None
		return self.align.comp

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.align = None
		_hx_o.flags = None
		_hx_o.builder = None
		_hx_o.row_map = None
		_hx_o.col_map = None
		_hx_o.has_parent = None
		_hx_o.a = None
		_hx_o.b = None
		_hx_o.p = None
		_hx_o.rp_header = None
		_hx_o.ra_header = None
		_hx_o.rb_header = None
		_hx_o.is_index_p = None
		_hx_o.is_index_a = None
		_hx_o.is_index_b = None
		_hx_o.order = None
		_hx_o.row_units = None
		_hx_o.column_units = None
		_hx_o.show_rc_numbers = None
		_hx_o.row_moves = None
		_hx_o.col_moves = None
		_hx_o.active_row = None
		_hx_o.active_column = None
		_hx_o.allow_insert = None
		_hx_o.allow_delete = None
		_hx_o.allow_update = None
		_hx_o.v = None
		_hx_o.sep = None
		_hx_o.conflict_sep = None
		_hx_o.schema = None
		_hx_o.have_schema = None
		_hx_o.top_line_done = None
		_hx_o.have_addition = None
		_hx_o.act = None
		_hx_o.publish = None
		_hx_o.diff_found = None
		_hx_o.schema_diff_found = None
		_hx_o.preserve_columns = None
		_hx_o.nested = None
		_hx_o.nesting_present = None


TableDiff = _hx_classes.registerClass("TableDiff", fields=["align","flags","builder","row_map","col_map","has_parent","a","b","p","rp_header","ra_header","rb_header","is_index_p","is_index_a","is_index_b","order","row_units","column_units","show_rc_numbers","row_moves","col_moves","active_row","active_column","allow_insert","allow_delete","allow_update","v","sep","conflict_sep","schema","have_schema","top_line_done","have_addition","act","publish","diff_found","schema_diff_found","preserve_columns","nested","nesting_present"], methods=["setCellBuilder","getSeparator","quoteForDiff","isReordered","spreadContext","setIgnore","countActive","reset","setupTables","scanActivity","setupColumns","setupMoves","scanSchema","checkRcNumbers","addRcNumbers","elideColumns","addSchema","addHeader","checkMeta","getMetaTable","addMeta","refineActivity","normalizeString","isEqual","checkNesting","scanRow","hilite","hiliteSingle","hiliteWithNesting","hasDifference","hasSchemaDifference","isNested","getComparisonState"])(TableDiff)

class TableIO(object):

	def __init__(self):
		pass

	def valid(self):
		return True

	def getContent(self,name):
		return sys_io_File.getContent(name)

	def saveContent(self,name,txt):
		sys_io_File.saveContent(name,txt)
		return True

	def args(self):
		return Sys.args()

	def writeStdout(self,txt):
		(python_lib_Sys.stdout.buffer if hasattr(python_lib_Sys.stdout,"buffer") else python_lib_Sys.stdout).write(txt.encode("utf-8", "strict"))

	def writeStderr(self,txt):
		Sys.stderr().writeString(txt)

	def command(self,cmd,args):
		try:
			return Sys.command(cmd,args)
		except Exception as _hx_e:
			_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
			e = _hx_e1
			return 1

	def async(self):
		return False

	def exists(self,path):
		return sys_FileSystem.exists(path)

	def isTtyKnown(self):
		return True

	def isTty(self):
		if __import__('sys').stdout.isatty():
			return True
		if (Sys.getEnv("GIT_PAGER_IN_USE") == "true"):
			return True
		return False

	def openSqliteDatabase(self,path):
		return SqliteDatabase(sqlite3.connect(path),path)
		return None

	def sendToBrowser(self,html):
		haxe_Log.trace("do not know how to send to browser in this language",_hx_AnonObject({'fileName': "TableIO.hx", 'lineNumber': 189, 'className': "TableIO", 'methodName': "sendToBrowser"}))

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
TableIO = _hx_classes.registerClass("TableIO", methods=["valid","getContent","saveContent","args","writeStdout","writeStderr","command","async","exists","isTtyKnown","isTty","openSqliteDatabase","sendToBrowser"])(TableIO)

class TableModifier(object):

	def __init__(self,t):
		self.t = None
		self.t = t

	def removeColumn(self,at):
		fate = []
		_g1 = 0
		_g = self.t.get_width()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (i < at):
				fate.append(i)
				python_lib_Builtin.len(fate)
			elif (i > at):
				fate.append((i - 1))
				python_lib_Builtin.len(fate)
			else:
				fate.append(-1)
				python_lib_Builtin.len(fate)
		return self.t.insertOrDeleteColumns(fate,(self.t.get_width() - 1))

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.t = None


TableModifier = _hx_classes.registerClass("TableModifier", fields=["t"], methods=["removeColumn"])(TableModifier)

class TableStream(object):

	def __init__(self,t):
		self.t = None
		self.at = None
		self.h = None
		self.src = None
		self.columns = None
		self.row = None
		self.t = t
		self.at = -1
		self.h = t.get_height()
		self.src = None
		if (self.h < 0):
			meta = t.getMeta()
			if (meta is None):
				raise _HxException("Cannot get meta information for table")
			self.src = meta.getRowStream()
			if (self.src is None):
				raise _HxException("Cannot iterate table")

	def fetchColumns(self):
		if (self.columns is not None):
			return self.columns
		if (self.src is not None):
			self.columns = self.src.fetchColumns()
			return self.columns
		self.columns = list()
		_g1 = 0
		_g = self.t.get_width()
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			_this = self.columns
			x = self.t.getCell(i,0)
			_this.append(x)
			python_lib_Builtin.len(_this)
		return self.columns

	def fetchRow(self):
		if (self.src is not None):
			return self.src.fetchRow()
		if (self.at >= self.h):
			return None
		row = haxe_ds_StringMap()
		_g1 = 0
		_g = python_lib_Builtin.len(self.columns)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			v = self.t.getCell(i,self.at)
			value = v
			row.h[(self.columns[i] if i >= 0 and i < python_lib_Builtin.len(self.columns) else None)] = value
			v
		return row

	def fetch(self):
		if (self.at == -1):
			_hx_local_0 = self
			_hx_local_1 = _hx_local_0.at
			_hx_local_0.at = (_hx_local_1 + 1)
			_hx_local_1
			if (self.src is not None):
				self.fetchColumns()
			return True
		if (self.src is not None):
			self.at = 1
			self.row = self.fetchRow()
			return (self.row is not None)
		_hx_local_2 = self
		_hx_local_3 = _hx_local_2.at
		_hx_local_2.at = (_hx_local_3 + 1)
		_hx_local_3
		return (self.at < self.h)

	def getCell(self,x):
		if (self.at == 0):
			return (self.columns[x] if x >= 0 and x < python_lib_Builtin.len(self.columns) else None)
		if (self.row is not None):
			return self.row.h.get((self.columns[x] if x >= 0 and x < python_lib_Builtin.len(self.columns) else None),None)
		return self.t.getCell(x,self.at)

	def width(self):
		self.fetchColumns()
		return python_lib_Builtin.len(self.columns)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.t = None
		_hx_o.at = None
		_hx_o.h = None
		_hx_o.src = None
		_hx_o.columns = None
		_hx_o.row = None


TableStream = _hx_classes.registerClass("TableStream", fields=["t","at","h","src","columns","row"], methods=["fetchColumns","fetchRow","fetch","getCell","width"], interfaces=[RowStream])(TableStream)

class Tables(object):

	def __init__(self,template):
		self.template = None
		self.tables = None
		self.table_order = None
		self.alignment = None
		self.template = template
		self.tables = haxe_ds_StringMap()
		self.table_order = list()

	def add(self,name):
		t = self.template.clone()
		self.tables.h[name] = t
		_this = self.table_order
		_this.append(name)
		python_lib_Builtin.len(_this)
		return t

	def getOrder(self):
		return self.table_order

	def get(self,name):
		return self.tables.h.get(name,None)

	def one(self):
		return self.tables.h.get((self.table_order[0] if 0 < python_lib_Builtin.len(self.table_order) else None),None)

	def hasInsDel(self):
		if (self.alignment is None):
			return False
		if self.alignment.has_addition:
			return True
		if self.alignment.has_removal:
			return True
		return False

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.template = None
		_hx_o.tables = None
		_hx_o.table_order = None
		_hx_o.alignment = None


Tables = _hx_classes.registerClass("Tables", fields=["template","tables","table_order","alignment"], methods=["add","getOrder","get","one","hasInsDel"])(Tables)

class TerminalDiffRender(object):

	def __init__(self,flags = None):
		self.codes = None
		self.t = None
		self.csv = None
		self.v = None
		self.align_columns = None
		self.wide_columns = None
		self.flags = None
		self.align_columns = True
		self.wide_columns = False
		self.flags = flags
		if (flags is not None):
			if (flags.padding_strategy == "dense"):
				self.align_columns = False
			if (flags.padding_strategy == "sparse"):
				self.wide_columns = True

	def alignColumns(self,enable):
		self.align_columns = enable

	def render(self,t):
		self.csv = Csv()
		result = ""
		w = t.get_width()
		h = t.get_height()
		txt = ""
		self.t = t
		self.v = t.getCellView()
		self.codes = haxe_ds_StringMap()
		self.codes.h["header"] = "\x1B[0;1m"
		self.codes.h["meta"] = "\x1B[0;1m"
		self.codes.h["spec"] = "\x1B[35;1m"
		self.codes.h["add"] = "\x1B[32;1m"
		self.codes.h["conflict"] = "\x1B[33;1m"
		self.codes.h["modify"] = "\x1B[34;1m"
		self.codes.h["remove"] = "\x1B[31;1m"
		self.codes.h["minor"] = "\x1B[2m"
		self.codes.h["done"] = "\x1B[0m"
		sizes = None
		if self.align_columns:
			sizes = self.pickSizes(t)
		_g = 0
		while ((_g < h)):
			y = _g
			_g = (_g + 1)
			target = 0
			at = 0
			_g1 = 0
			while ((_g1 < w)):
				x = _g1
				_g1 = (_g1 + 1)
				if (x > 0):
					txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull((((HxOverrides.stringOrNull(self.codes.h.get("minor",None)) + ",") + HxOverrides.stringOrNull(self.codes.h.get("done",None))))))
				if (sizes is not None):
					spaces = (target - at)
					_g2 = 0
					while ((_g2 < spaces)):
						i = _g2
						_g2 = (_g2 + 1)
						txt = (HxOverrides.stringOrNull(txt) + " ")
						at = (at + 1)
				txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(self.getText(x,y,True)))
				if (sizes is not None):
					bit = self.getText(x,y,False)
					at = (at + python_lib_Builtin.len(bit))
					target = (target + (sizes[x] if x >= 0 and x < python_lib_Builtin.len(sizes) else None))
			txt = (HxOverrides.stringOrNull(txt) + "\r\n")
		self.t = None
		self.v = None
		self.csv = None
		self.codes = None
		return txt

	def getText(self,x,y,color):
		val = self.t.getCell(x,y)
		cell = DiffRender.renderCell(self.t,self.v,x,y)
		if color:
			code = None
			if (cell.category is not None):
				code = self.codes.h.get(cell.category,None)
			if (cell.category_given_tr is not None):
				code_tr = self.codes.h.get(cell.category_given_tr,None)
				if (code_tr is not None):
					code = code_tr
			if (code is not None):
				if (cell.rvalue is not None):
					val = ((((((HxOverrides.stringOrNull(self.codes.h.get("remove",None)) + HxOverrides.stringOrNull(cell.lvalue)) + HxOverrides.stringOrNull(self.codes.h.get("modify",None))) + HxOverrides.stringOrNull(cell.pretty_separator)) + HxOverrides.stringOrNull(self.codes.h.get("add",None))) + HxOverrides.stringOrNull(cell.rvalue)) + HxOverrides.stringOrNull(self.codes.h.get("done",None)))
					if (cell.pvalue is not None):
						val = ((((HxOverrides.stringOrNull(self.codes.h.get("conflict",None)) + HxOverrides.stringOrNull(cell.pvalue)) + HxOverrides.stringOrNull(self.codes.h.get("modify",None))) + HxOverrides.stringOrNull(cell.pretty_separator)) + Std.string(val))
				else:
					val = cell.pretty_value
					val = ((HxOverrides.stringOrNull(code) + Std.string(val)) + HxOverrides.stringOrNull(self.codes.h.get("done",None)))
		else:
			val = cell.pretty_value
		return self.csv.renderCell(self.v,val)

	def pickSizes(self,t):
		w = t.get_width()
		h = t.get_height()
		v = t.getCellView()
		csv = Csv()
		sizes = list()
		row = -1
		total = (w - 1)
		_g = 0
		while ((_g < w)):
			x = _g
			_g = (_g + 1)
			m = 0
			m2 = 0
			mmax = 0
			mmostmax = 0
			mmin = -1
			_g1 = 0
			while ((_g1 < h)):
				y = _g1
				_g1 = (_g1 + 1)
				txt = self.getText(x,y,False)
				if ((txt == "@@") and ((row == -1))):
					row = y
				len = python_lib_Builtin.len(txt)
				if (y == row):
					mmin = len
				m = (m + len)
				m2 = (m2 + ((len * len)))
				if (len > mmax):
					mmax = len
			mean = (m / h)
			stddev = None
			v1 = ((m2 / h) - ((mean * mean)))
			if (v1 < 0):
				stddev = Math.NaN
			else:
				stddev = python_lib_Math.sqrt(v1)
			most = None
			def _hx_local_3():
				_hx_local_2 = None
				try:
					_hx_local_2 = python_lib_Builtin.int(((mean + ((stddev * 2))) + 0.5))
				except Exception as _hx_e:
					_hx_e1 = _hx_e.val if isinstance(_hx_e, _HxException) else _hx_e
					e = _hx_e1
					_hx_local_2 = None
				return _hx_local_2
			most = _hx_local_3()
			_g11 = 0
			while ((_g11 < h)):
				y1 = _g11
				_g11 = (_g11 + 1)
				txt1 = self.getText(x,y1,False)
				len1 = python_lib_Builtin.len(txt1)
				if (len1 <= most):
					if (len1 > mmostmax):
						mmostmax = len1
			full = mmax
			most = mmostmax
			if (mmin != -1):
				if (most < mmin):
					most = mmin
			if self.wide_columns:
				most = full
			sizes.append(most)
			python_lib_Builtin.len(sizes)
			total = (total + most)
		if (total > 130):
			return None
		return sizes

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.codes = None
		_hx_o.t = None
		_hx_o.csv = None
		_hx_o.v = None
		_hx_o.align_columns = None
		_hx_o.wide_columns = None
		_hx_o.flags = None

TerminalDiffRender = _hx_classes.registerClass("TerminalDiffRender", fields=["codes","t","csv","v","align_columns","wide_columns","flags"], methods=["alignColumns","render","getText","pickSizes"])(TerminalDiffRender)

class ValueType(Enum):
	def __init__(self, t, i, p):
		super(ValueType,self).__init__(t, i, p)

	@staticmethod
	def TClass(c):
		return ValueType("TClass", 6, [c])

	@staticmethod
	def TEnum(e):
		return ValueType("TEnum", 7, [e])
ValueType = _hx_classes.registerEnum("ValueType", ["TNull","TInt","TFloat","TBool","TObject","TFunction","TClass","TEnum","TUnknown"])(ValueType)

ValueType.TNull = ValueType("TNull", 0, list())
ValueType.TInt = ValueType("TInt", 1, list())
ValueType.TFloat = ValueType("TFloat", 2, list())
ValueType.TBool = ValueType("TBool", 3, list())
ValueType.TObject = ValueType("TObject", 4, list())
ValueType.TFunction = ValueType("TFunction", 5, list())
ValueType.TUnknown = ValueType("TUnknown", 8, list())


class Type(object):

	@staticmethod
	def typeof(v):
		if (v is None):
			return ValueType.TNull
		elif python_lib_Builtin.isinstance(v,python_lib_Builtin.bool):
			return ValueType.TBool
		elif python_lib_Builtin.isinstance(v,python_lib_Builtin.int):
			return ValueType.TInt
		elif python_lib_Builtin.isinstance(v,python_lib_Builtin.float):
			return ValueType.TFloat
		elif python_lib_Builtin.isinstance(v,String):
			return ValueType.TClass(String)
		elif python_lib_Builtin.isinstance(v,list):
			return ValueType.TClass(list)
		elif (python_lib_Builtin.isinstance(v,_hx_AnonObject) or python_lib_Inspect.isclass(v)):
			return ValueType.TObject
		elif python_lib_Builtin.isinstance(v,Enum):
			return ValueType.TEnum(v.__class__)
		elif (python_lib_Builtin.isinstance(v,python_lib_Builtin.type) or python_lib_Builtin.hasattr(v,"_hx_class")):
			return ValueType.TClass(v.__class__)
		elif python_lib_Builtin.callable(v):
			return ValueType.TFunction
		else:
			return ValueType.TUnknown


Type = _hx_classes.registerClass("Type", statics=["typeof"])(Type)

class Unit(object):

	def __init__(self,l = -2,r = -2,p = -2):
		if (l is None):
			l = -2
		if (r is None):
			r = -2
		if (p is None):
			p = -2
		self.l = None
		self.r = None
		self.p = None
		self.l = l
		self.r = r
		self.p = p

	def lp(self):
		if (self.p == -2):
			return self.l
		else:
			return self.p

	def toString(self):
		if (self.p >= -1):
			return ((((HxOverrides.stringOrNull(Unit.describe(self.p)) + "|") + HxOverrides.stringOrNull(Unit.describe(self.l))) + ":") + HxOverrides.stringOrNull(Unit.describe(self.r)))
		return ((HxOverrides.stringOrNull(Unit.describe(self.l)) + ":") + HxOverrides.stringOrNull(Unit.describe(self.r)))

	def fromString(self,txt):
		txt = (HxOverrides.stringOrNull(txt) + "]")
		at = 0
		_g1 = 0
		_g = python_lib_Builtin.len(txt)
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			ch = HxString.charCodeAt(txt,i)
			if ((ch >= 48) and ((ch <= 57))):
				at = (at * 10)
				at = (at + ((ch - 48)))
			elif (ch == 45):
				at = -1
			elif (ch == 124):
				self.p = at
				at = 0
			elif (ch == 58):
				self.l = at
				at = 0
			elif (ch == 93):
				self.r = at
				return True
		return False

	def base26(self,num):
		alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		if (num < 0):
			return "-"
		out = ""
		while True:
			def _hx_local_0():
				index = (num % 26)
				return ("" if (((index < 0) or ((index >= python_lib_Builtin.len(alpha))))) else alpha[index])
			out = (HxOverrides.stringOrNull(out) + HxOverrides.stringOrNull(_hx_local_0()))
			num = (Math.floor((num / 26)) - 1)
			if (not ((num >= 0))):
				break
		return out

	def toBase26String(self):
		if (self.p >= -1):
			return ((((HxOverrides.stringOrNull(self.base26(self.p)) + "|") + HxOverrides.stringOrNull(self.base26(self.l))) + ":") + HxOverrides.stringOrNull(self.base26(self.r)))
		return ((HxOverrides.stringOrNull(self.base26(self.l)) + ":") + HxOverrides.stringOrNull(self.base26(self.r)))

	@staticmethod
	def describe(i):
		if (i >= 0):
			return ("" + Std.string(i))
		else:
			return "-"

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.l = None
		_hx_o.r = None
		_hx_o.p = None


Unit = _hx_classes.registerClass("Unit", fields=["l","r","p"], methods=["lp","toString","fromString","base26","toBase26String"], statics=["describe"])(Unit)

class Viterbi(object):

	def __init__(self):
		self.K = None
		self.T = None
		self.index = None
		self.mode = None
		self.path_valid = None
		self.best_cost = None
		self.cost = None
		self.src = None
		self.path = None
		def _hx_local_0():
			self.T = 0
			return self.T
		self.K = _hx_local_0()
		self.reset()
		self.cost = SparseSheet()
		self.src = SparseSheet()
		self.path = SparseSheet()

	def reset(self):
		self.index = 0
		self.mode = 0
		self.path_valid = False
		self.best_cost = 0

	def setSize(self,states,sequence_length):
		self.K = states
		self.T = sequence_length
		self.cost.resize(self.K,self.T,0)
		self.src.resize(self.K,self.T,-1)
		self.path.resize(1,self.T,-1)

	def assertMode(self,next):
		if ((next == 0) and ((self.mode == 1))):
			_hx_local_0 = self
			_hx_local_1 = _hx_local_0.index
			_hx_local_0.index = (_hx_local_1 + 1)
			_hx_local_1
		self.mode = next

	def addTransition(self,s0,s1,c):
		resize = False
		if (s0 >= self.K):
			self.K = (s0 + 1)
			resize = True
		if (s1 >= self.K):
			self.K = (s1 + 1)
			resize = True
		if resize:
			self.cost.nonDestructiveResize(self.K,self.T,0)
			self.src.nonDestructiveResize(self.K,self.T,-1)
			self.path.nonDestructiveResize(1,self.T,-1)
		self.path_valid = False
		self.assertMode(1)
		if (self.index >= self.T):
			self.T = (self.index + 1)
			self.cost.nonDestructiveResize(self.K,self.T,0)
			self.src.nonDestructiveResize(self.K,self.T,-1)
			self.path.nonDestructiveResize(1,self.T,-1)
		sourced = False
		if (self.index > 0):
			c = (c + self.cost.get(s0,(self.index - 1)))
			sourced = (self.src.get(s0,(self.index - 1)) != -1)
		else:
			sourced = True
		if sourced:
			if ((c < self.cost.get(s1,self.index)) or ((self.src.get(s1,self.index) == -1))):
				self.cost.set(s1,self.index,c)
				self.src.set(s1,self.index,s0)

	def endTransitions(self):
		self.path_valid = False
		self.assertMode(0)

	def beginTransitions(self):
		self.path_valid = False
		self.assertMode(1)

	def calculatePath(self):
		if self.path_valid:
			return
		self.endTransitions()
		best = 0
		bestj = -1
		if (self.index <= 0):
			self.path_valid = True
			return
		_g1 = 0
		_g = self.K
		while ((_g1 < _g)):
			j = _g1
			_g1 = (_g1 + 1)
			if ((((self.cost.get(j,(self.index - 1)) < best) or ((bestj == -1)))) and ((self.src.get(j,(self.index - 1)) != -1))):
				best = self.cost.get(j,(self.index - 1))
				bestj = j
		self.best_cost = best
		_g11 = 0
		_g2 = self.index
		while ((_g11 < _g2)):
			j1 = _g11
			_g11 = (_g11 + 1)
			i = ((self.index - 1) - j1)
			self.path.set(0,i,bestj)
			if (not (((bestj != -1) and (((bestj >= 0) and ((bestj < self.K))))))):
				haxe_Log.trace("Problem in Viterbi",_hx_AnonObject({'fileName': "Viterbi.hx", 'lineNumber': 167, 'className': "Viterbi", 'methodName': "calculatePath"}))
			bestj = self.src.get(bestj,i)
		self.path_valid = True

	def toString(self):
		self.calculatePath()
		txt = ""
		_g1 = 0
		_g = self.index
		while ((_g1 < _g)):
			i = _g1
			_g1 = (_g1 + 1)
			if (self.path.get(0,i) == -1):
				txt = (HxOverrides.stringOrNull(txt) + "*")
			else:
				txt = (HxOverrides.stringOrNull(txt) + Std.string(self.path.get(0,i)))
			if (self.K >= 10):
				txt = (HxOverrides.stringOrNull(txt) + " ")
		txt = (HxOverrides.stringOrNull(txt) + HxOverrides.stringOrNull(((" costs " + Std.string(self.getCost())))))
		return txt

	def length(self):
		if (self.index > 0):
			self.calculatePath()
		return self.index

	def get(self,i):
		self.calculatePath()
		return self.path.get(0,i)

	def getCost(self):
		self.calculatePath()
		return self.best_cost

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.K = None
		_hx_o.T = None
		_hx_o.index = None
		_hx_o.mode = None
		_hx_o.path_valid = None
		_hx_o.best_cost = None
		_hx_o.cost = None
		_hx_o.src = None
		_hx_o.path = None


Viterbi = _hx_classes.registerClass("Viterbi", fields=["K","T","index","mode","path_valid","best_cost","cost","src","path"], methods=["reset","setSize","assertMode","addTransition","endTransitions","beginTransitions","calculatePath","toString","length","get","getCost"])(Viterbi)

class haxe_Log(object):

	@staticmethod
	def trace(v,infos = None):
		unicode = None
		if (infos is not None):
			unicode = ((((HxOverrides.stringOrNull(infos.fileName) + ":") + Std.string(infos.lineNumber)) + ": ") + Std.string(v))
			if (Reflect.field(infos,"customParams") is not None):
				unicode = (HxOverrides.stringOrNull(unicode) + HxOverrides.stringOrNull((("," + HxOverrides.stringOrNull(",".join([python_Boot.toString1(x1,'') for x1 in Reflect.field(infos,"customParams")]))))))
		else:
			unicode = v
		python_Lib.println(unicode)


haxe_Log = _hx_classes.registerClass("haxe.Log", statics=["trace"])(haxe_Log)

class haxe_ds_IntMap(object):

	def __init__(self):
		self.h = None
		self.h = python_lib_Dict()

	def set(self,key,value):
		self.h[key] = value

	def get(self,key):
		return self.h.get(key,None)

	def remove(self,key):
		if (not key in self.h):
			return False
		del self.h[key]
		return True

	def keys(self):
		this1 = None
		_this = self.h.keys()
		this1 = python_lib_Builtin.iter(_this)
		return python_HaxeIterator(this1)

	def toString(self):
		s_b = python_lib_io_StringIO()
		s_b.write("{")
		it = self.keys()
		_hx_local_0 = it
		while (_hx_local_0.hasNext()):
			i = hxnext(_hx_local_0)
			s_b.write(Std.string(i))
			s_b.write(" => ")
			x = Std.string(self.h.get(i,None))
			s_b.write(Std.string(x))
			if it.hasNext():
				s_b.write(", ")
		s_b.write("}")
		return s_b.getvalue()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.h = None


haxe_ds_IntMap = _hx_classes.registerClass("haxe.ds.IntMap", fields=["h"], methods=["set","get","remove","keys","toString"], interfaces=[haxe_IMap])(haxe_ds_IntMap)

class haxe_format_JsonPrinter(object):

	def __init__(self,replacer,space):
		self.buf = None
		self.replacer = None
		self.indent = None
		self.pretty = None
		self.nind = None
		self.replacer = replacer
		self.indent = space
		self.pretty = (space is not None)
		self.nind = 0
		self.buf = StringBuf()

	def write(self,k,v):
		if (self.replacer is not None):
			v = self.replacer(k,v)
		_g = Type.typeof(v)
		if ((_g.index) == 8):
			self.buf.b.write("\"???\"")
		elif ((_g.index) == 4):
			self.fieldsString(v,python_Boot.fields(v))
		elif ((_g.index) == 1):
			v1 = v
			self.buf.b.write(Std.string(v1))
		elif ((_g.index) == 2):
			v2 = None
			def _hx_local_0():
				f = v
				return (((f != Math.POSITIVE_INFINITY) and ((f != Math.NEGATIVE_INFINITY))) and (not python_lib_Math.isnan(f)))
			if _hx_local_0():
				v2 = v
			else:
				v2 = "null"
			self.buf.b.write(Std.string(v2))
		elif ((_g.index) == 5):
			self.buf.b.write("\"<fun>\"")
		elif ((_g.index) == 6):
			c = _g.params[0]
			if (c == String):
				self.quote(v)
			elif (c == list):
				v3 = v
				s = "".join(python_lib_Builtin.map(hxunichr,[91]))
				self.buf.b.write(s)
				len = python_lib_Builtin.len(v3)
				last = (len - 1)
				_g1 = 0
				while ((_g1 < len)):
					i = _g1
					_g1 = (_g1 + 1)
					if (i > 0):
						s1 = "".join(python_lib_Builtin.map(hxunichr,[44]))
						self.buf.b.write(s1)
					else:
						_hx_local_1 = self
						_hx_local_2 = _hx_local_1.nind
						_hx_local_1.nind = (_hx_local_2 + 1)
						_hx_local_2
					if self.pretty:
						s2 = "".join(python_lib_Builtin.map(hxunichr,[10]))
						self.buf.b.write(s2)
					if self.pretty:
						v4 = StringTools.lpad("",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
						self.buf.b.write(Std.string(v4))
					self.write(i,(v3[i] if i >= 0 and i < python_lib_Builtin.len(v3) else None))
					if (i == last):
						_hx_local_3 = self
						_hx_local_4 = _hx_local_3.nind
						_hx_local_3.nind = (_hx_local_4 - 1)
						_hx_local_4
						if self.pretty:
							s3 = "".join(python_lib_Builtin.map(hxunichr,[10]))
							self.buf.b.write(s3)
						if self.pretty:
							v5 = StringTools.lpad("",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
							self.buf.b.write(Std.string(v5))
				s4 = "".join(python_lib_Builtin.map(hxunichr,[93]))
				self.buf.b.write(s4)
			elif (c == haxe_ds_StringMap):
				v6 = v
				o = _hx_AnonObject({})
				_hx_local_5 = v6.keys()
				while (_hx_local_5.hasNext()):
					k1 = hxnext(_hx_local_5)
					value = v6.h.get(k1,None)
					python_lib_Builtin.setattr(o,(("_hx_" + k1) if (k1 in python_Boot.keywords) else (("_hx_" + k1) if (((((python_lib_Builtin.len(k1) > 2) and ((python_lib_Builtin.ord(k1[0]) == 95))) and ((python_lib_Builtin.ord(k1[1]) == 95))) and ((python_lib_Builtin.ord(k1[(python_lib_Builtin.len(k1) - 1)]) != 95)))) else k1)),value)
				self.fieldsString(o,python_Boot.fields(o))
			elif (c == Date):
				v7 = v
				self.quote(v7.toString())
			else:
				self.fieldsString(v,python_Boot.fields(v))
		elif ((_g.index) == 7):
			i1 = None
			e = v
			i1 = e.index
			v8 = i1
			self.buf.b.write(Std.string(v8))
		elif ((_g.index) == 3):
			v9 = v
			self.buf.b.write(Std.string(v9))
		elif ((_g.index) == 0):
			self.buf.b.write("null")
		else:
			pass

	def fieldsString(self,v,fields):
		s = "".join(python_lib_Builtin.map(hxunichr,[123]))
		self.buf.b.write(s)
		len = python_lib_Builtin.len(fields)
		last = (len - 1)
		first = True
		_g = 0
		while ((_g < len)):
			i = _g
			_g = (_g + 1)
			f = (fields[i] if i >= 0 and i < python_lib_Builtin.len(fields) else None)
			value = python_Boot.field(v,f)
			if Reflect.isFunction(value):
				continue
			if first:
				_hx_local_0 = self
				_hx_local_1 = _hx_local_0.nind
				_hx_local_0.nind = (_hx_local_1 + 1)
				_hx_local_1
				first = False
			else:
				s1 = "".join(python_lib_Builtin.map(hxunichr,[44]))
				self.buf.b.write(s1)
			if self.pretty:
				s2 = "".join(python_lib_Builtin.map(hxunichr,[10]))
				self.buf.b.write(s2)
			if self.pretty:
				v1 = StringTools.lpad("",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
				self.buf.b.write(Std.string(v1))
			self.quote(f)
			s3 = "".join(python_lib_Builtin.map(hxunichr,[58]))
			self.buf.b.write(s3)
			if self.pretty:
				s4 = "".join(python_lib_Builtin.map(hxunichr,[32]))
				self.buf.b.write(s4)
			self.write(f,value)
			if (i == last):
				_hx_local_2 = self
				_hx_local_3 = _hx_local_2.nind
				_hx_local_2.nind = (_hx_local_3 - 1)
				_hx_local_3
				if self.pretty:
					s5 = "".join(python_lib_Builtin.map(hxunichr,[10]))
					self.buf.b.write(s5)
				if self.pretty:
					v2 = StringTools.lpad("",self.indent,(self.nind * python_lib_Builtin.len(self.indent)))
					self.buf.b.write(Std.string(v2))
		s6 = "".join(python_lib_Builtin.map(hxunichr,[125]))
		self.buf.b.write(s6)

	def quote(self,s):
		s1 = "".join(python_lib_Builtin.map(hxunichr,[34]))
		self.buf.b.write(s1)
		i = 0
		while (True):
			c = None
			index = i
			i = (i + 1)
			if (index >= python_lib_Builtin.len(s)):
				c = -1
			else:
				c = python_lib_Builtin.ord(s[index])
			if (c == -1):
				break
			if ((c) == 34):
				self.buf.b.write("\\\"")
			elif ((c) == 92):
				self.buf.b.write("\\\\")
			elif ((c) == 10):
				self.buf.b.write("\\n")
			elif ((c) == 13):
				self.buf.b.write("\\r")
			elif ((c) == 9):
				self.buf.b.write("\\t")
			elif ((c) == 8):
				self.buf.b.write("\\b")
			elif ((c) == 12):
				self.buf.b.write("\\f")
			else:
				s2 = "".join(python_lib_Builtin.map(hxunichr,[c]))
				self.buf.b.write(s2)
		s3 = "".join(python_lib_Builtin.map(hxunichr,[34]))
		self.buf.b.write(s3)

	@staticmethod
	def _hx_print(o,replacer = None,space = None):
		printer = haxe_format_JsonPrinter(replacer, space)
		printer.write("",o)
		return printer.buf.b.getvalue()

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.buf = None
		_hx_o.replacer = None
		_hx_o.indent = None
		_hx_o.pretty = None
		_hx_o.nind = None


haxe_format_JsonPrinter = _hx_classes.registerClass("haxe.format.JsonPrinter", fields=["buf","replacer","indent","pretty","nind"], methods=["write","fieldsString","quote"], statics=["print"])(haxe_format_JsonPrinter)

class haxe_io_Bytes(object):

	def __init__(self,length,b):
		self.length = None
		self.b = None
		self.length = length
		self.b = b

	@staticmethod
	def ofString(s):
		b = python_lib_Builtin.bytearray(s,"UTF-8")
		return haxe_io_Bytes(python_lib_Builtin.len(b), b)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.length = None
		_hx_o.b = None


haxe_io_Bytes = _hx_classes.registerClass("haxe.io.Bytes", fields=["length","b"], statics=["ofString"])(haxe_io_Bytes)

class haxe_io_Output(object):

	def writeByte(self,c):
		raise _HxException("Not implemented")

	def writeBytes(self,s,pos,len):
		k = len
		b = s.b
		if (((pos < 0) or ((len < 0))) or (((pos + len) > s.length))):
			raise _HxException(haxe_io_Error.OutsideBounds)
		while ((k > 0)):
			self.writeByte(b[pos])
			pos = (pos + 1)
			k = (k - 1)
		return len

	def writeFullBytes(self,s,pos,len):
		while ((len > 0)):
			k = self.writeBytes(s,pos,len)
			pos = (pos + k)
			len = (len - k)

	def writeString(self,s):
		b = haxe_io_Bytes.ofString(s)
		self.writeFullBytes(b,0,b.length)

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
haxe_io_Output = _hx_classes.registerClass("haxe.io.Output", methods=["writeByte","writeBytes","writeFullBytes","writeString"])(haxe_io_Output)

class haxe_io_Eof(object):

	def toString(self):
		return "Eof"

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
haxe_io_Eof = _hx_classes.registerClass("haxe.io.Eof", methods=["toString"])(haxe_io_Eof)

class haxe_io_Error(Enum):
	def __init__(self, t, i, p):
		super(haxe_io_Error,self).__init__(t, i, p)

	@staticmethod
	def Custom(e):
		return haxe_io_Error("Custom", 3, [e])
haxe_io_Error = _hx_classes.registerEnum("haxe.io.Error", ["Blocked","Overflow","OutsideBounds","Custom"])(haxe_io_Error)

haxe_io_Error.Blocked = haxe_io_Error("Blocked", 0, list())
haxe_io_Error.Overflow = haxe_io_Error("Overflow", 1, list())
haxe_io_Error.OutsideBounds = haxe_io_Error("OutsideBounds", 2, list())


class python_Lib(object):

	@staticmethod
	def println(v):
		unicode = Std.string(v)
		python_lib_Sys.stdout.buffer.write((("" + HxOverrides.stringOrNull(unicode)) + "\n").encode("utf-8", "strict"))
		python_lib_Sys.stdout.flush()

	@staticmethod
	def dictToAnon(v):
		return _hx_AnonObject(v.copy())


python_Lib = _hx_classes.registerClass("python.Lib", statics=["println","dictToAnon"])(python_Lib)

class python_NativeStringTools(object):

	@staticmethod
	def encode(s,encoding = "utf-8",errors = "strict"):
		if (encoding is None):
			encoding = "utf-8"
		if (errors is None):
			errors = "strict"
		return s.encode(encoding, errors)


python_NativeStringTools = _hx_classes.registerClass("python.NativeStringTools", statics=["encode"])(python_NativeStringTools)

class _HxException(Exception):

	def __init__(self,val):
		self.val = None
		message = Std.string(val)
		super(_HxException, self).__init__(message)
		self.val = val

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.val = None


_HxException = _hx_classes.registerClass("_HxException", fields=["val"], superClass=Exception)(_HxException)

class HxString(object):

	@staticmethod
	def split(s,d):
		if (d == ""):
			return python_lib_Builtin.list(s)
		else:
			return s.split(d)

	@staticmethod
	def charCodeAt(s,index):
		if ((((s is None) or ((python_lib_Builtin.len(s) == 0))) or ((index < 0))) or ((index >= python_lib_Builtin.len(s)))):
			return None
		else:
			return python_lib_Builtin.ord(s[index])

	@staticmethod
	def charAt(s,index):
		if ((index < 0) or ((index >= python_lib_Builtin.len(s)))):
			return ""
		else:
			return s[index]

	@staticmethod
	def lastIndexOf(s,unicode,startIndex = None):
		if (startIndex is None):
			return s.rfind(unicode, 0, python_lib_Builtin.len(s))
		else:
			i = s.rfind(unicode, 0, (startIndex + 1))
			startLeft = None
			if (i == -1):
				startLeft = python_lib_Builtin.max(0,((startIndex + 1) - python_lib_Builtin.len(unicode)))
			else:
				startLeft = (i + 1)
			check = s.find(unicode, startLeft, python_lib_Builtin.len(s))
			if ((check > i) and ((check <= startIndex))):
				return check
			else:
				return i

	@staticmethod
	def toUpperCase(s):
		return s.upper()

	@staticmethod
	def toLowerCase(s):
		return s.lower()

	@staticmethod
	def indexOf(s,unicode,startIndex = None):
		if (startIndex is None):
			return s.find(unicode)
		else:
			return s.find(unicode, startIndex)

	@staticmethod
	def toString(s):
		return s

	@staticmethod
	def get_length(s):
		return python_lib_Builtin.len(s)

	@staticmethod
	def fromCharCode(code):
		return "".join(python_lib_Builtin.map(hxunichr,[code]))

	@staticmethod
	def substring(s,startIndex,endIndex = None):
		if (startIndex < 0):
			startIndex = 0
		if (endIndex is None):
			return s[startIndex:]
		else:
			if (endIndex < 0):
				endIndex = 0
			if (endIndex < startIndex):
				return s[endIndex:startIndex]
			else:
				return s[startIndex:endIndex]

	@staticmethod
	def substr(s,startIndex,len = None):
		if (len is None):
			return s[startIndex:]
		else:
			if (len == 0):
				return ""
			return s[startIndex:(startIndex + len)]


HxString = _hx_classes.registerClass("HxString", statics=["split","charCodeAt","charAt","lastIndexOf","toUpperCase","toLowerCase","indexOf","toString","get_length","fromCharCode","substring","substr"])(HxString)

class python_io_NativeOutput(haxe_io_Output):

	def __init__(self,stream):
		self.stream = None
		self.stream = stream



	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.stream = None


python_io_NativeOutput = _hx_classes.registerClass("python.io.NativeOutput", fields=["stream"], superClass=haxe_io_Output)(python_io_NativeOutput)

class python_io_IOutput(object):
	pass
python_io_IOutput = _hx_classes.registerClass("python.io.IOutput", methods=["writeByte","writeBytes","writeFullBytes","writeString"])(python_io_IOutput)

class python_io_IFileOutput(object):
	pass
python_io_IFileOutput = _hx_classes.registerClass("python.io.IFileOutput", interfaces=[python_io_IOutput])(python_io_IFileOutput)

class python_io_NativeTextOutput(python_io_NativeOutput):

	def __init__(self,stream):
		super(python_io_NativeTextOutput, self).__init__(stream)



	def writeByte(self,c):
		self.stream.write("".join(python_lib_Builtin.map(hxunichr,[c])))

	@staticmethod
	def _hx_empty_init(_hx_o):		pass
python_io_NativeTextOutput = _hx_classes.registerClass("python.io.NativeTextOutput", methods=["writeByte"], superClass=python_io_NativeOutput)(python_io_NativeTextOutput)

class python_io_FileTextOutput(python_io_NativeTextOutput):

	def __init__(self,stream):
		super(python_io_FileTextOutput, self).__init__(stream)


python_io_FileTextOutput = _hx_classes.registerClass("python.io.FileTextOutput", interfaces=[python_io_IFileOutput], superClass=python_io_NativeTextOutput)(python_io_FileTextOutput)

class python_io_IoTools(object):

	@staticmethod
	def createFileOutputFromText(t):
		return sys_io_FileOutput(python_io_FileTextOutput(t))


python_io_IoTools = _hx_classes.registerClass("python.io.IoTools", statics=["createFileOutputFromText"])(python_io_IoTools)

class sys_FileSystem(object):

	@staticmethod
	def exists(path):
		return python_lib_os_Path.exists(path)


sys_FileSystem = _hx_classes.registerClass("sys.FileSystem", statics=["exists"])(sys_FileSystem)

class sys_io_File(object):

	@staticmethod
	def getContent(path):
		f = codecs.open(path,"r","utf-8")
		content = f.read(-1)
		f.close()
		return content

	@staticmethod
	def saveContent(path,content):
		f = codecs.open(path,"w","utf-8")
		f.write(content)
		f.close()


sys_io_File = _hx_classes.registerClass("sys.io.File", statics=["getContent","saveContent"])(sys_io_File)

class sys_io_FileOutput(haxe_io_Output):

	def __init__(self,impl):
		self.impl = None
		self.impl = impl

	def writeByte(self,c):
		self.impl.writeByte(c)

	def writeBytes(self,s,pos,len):
		return self.impl.writeBytes(s,pos,len)

	def writeFullBytes(self,s,pos,len):
		self.impl.writeFullBytes(s,pos,len)

	def writeString(self,s):
		self.impl.writeString(s)

	@staticmethod
	def _hx_empty_init(_hx_o):
		_hx_o.impl = None
sys_io_FileOutput = _hx_classes.registerClass("sys.io.FileOutput", fields=["impl"], methods=["writeByte","writeBytes","writeFullBytes","writeString"], superClass=haxe_io_Output)(sys_io_FileOutput)

Math.NEGATIVE_INFINITY = python_lib_Builtin.float("-inf")
Math.POSITIVE_INFINITY = python_lib_Builtin.float("inf")
Math.NaN = python_lib_Builtin.float("nan")
Math.PI = python_lib_Math.pi
python_Boot.keywords = python_lib_Set(["and", "del", "from", "not", "while", "as", "elif", "global", "or", "with", "assert", "else", "if", "pass", "yield", "break", "except", "import", "print", "float", "class", "exec", "in", "raise", "continue", "finally", "is", "return", "def", "for", "lambda", "try", "None", "list", "True", "False"])
python_Boot.prefixLength = python_lib_Builtin.len("_hx_")
Coopy.VERSION = "1.3.17"
def _hx_init_Sys_environ():
	def _hx_local_0():
		Sys.environ = haxe_ds_StringMap()
		env = python_lib_Os.environ
		def _hx_local_1():
			_this = env.keys()
			def _hx_local_3():
				def _hx_local_2():
					this1 = python_lib_Builtin.iter(_this)
					return python_HaxeIterator(this1)
				return _hx_local_2()
			return _hx_local_3()
		_hx_local_4 = _hx_local_1()
		while (_hx_local_4.hasNext()):
			key = hxnext(_hx_local_4)
			value = env.get(key,None)
			Sys.environ.h[key] = value
		return Sys.environ
	return _hx_local_0()
Sys.environ = _hx_init_Sys_environ()

class PythonCellView(View):
    def __init__(self):
        pass

    def toString(self,d):
        return hxunicode(d) if (d!=None) else ""

    def equals(self,d1,d2):
        return hxunicode(d1) == hxunicode(d2)

    def toDatum(self,d):
        return d

    def makeHash(self):
        return {}

    def isHash(self,d):
        return type(d) is dict

    def hashSet(self,d,k,v):
        d[k] = v
        
    def hashGet(self,d,k):
        return d[k]

    def hashExists(self,d,k):
        return k in d


class PythonTableView(Table):
    def __init__(self,data):
        self.data = data
        self.height = len(data)
        self.width = 0
        if self.height>0:
            self.width = len(data[0])

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def getCell(self,x,y):
        return self.data[y][x]

    def setCell(self,x,y,c):
        self.data[y][x] = c

    def toString(self):
        return SimpleTable.tableToString(self)

    def getCellView(self):
        return PythonCellView()
        # return SimpleView()

    def isResizable(self):
        return True

    def resize(self,w,h):
        self.width = w
        self.height = h
        for i in hxrange(len(self.data)):
            row = self.data[i]
            if row == None:
                row = self.data[i] = []
            while len(row)<w:
                row.append(None)
        while len(self.data)<h:
            row = []
            for i in hxrange(w):
                row.append(None)
            self.data.append(row)
        return True

    def clear(self):
        for i in hxrange(len(self.data)):
            row = self.data[i]
            for j in hxrange(len(row)):
                row[j] = None
        self.width = 0
        self.height = 0

    def trimBlank(self): 
        return False

    def getData(self):
        return self.data

    def insertOrDeleteRows(self,fate,hfate):
        ndata = []
        for i in hxrange(len(fate)):
            j = fate[i];
            if j!=-1:
                if j>=len(ndata):
                    for k in hxrange(j-len(ndata)+1):
                        ndata.append(None)
                ndata[j] = self.data[i]

        del self.data[:]
        for i in hxrange(len(ndata)):
            self.data.append(ndata[i])
        self.resize(self.width,hfate)
        return True

    def insertOrDeleteColumns(self,fate,wfate):
        if wfate==self.width and wfate==len(fate):
            eq = True
            for i in hxrange(wfate):
                if fate[i]!=i:
                    eq = False
                    break
            if eq:
                return True

        for i in hxrange(self.height):
            row = self.data[i]
            nrow = []
            for j in hxrange(self.width):
                if fate[j]==-1:
                    continue
                at = fate[j]
                if at>=len(nrow):
                    for k in hxrange(at-len(nrow)+1):
                        nrow.append(None)
                nrow[at] = row[j]
            while len(nrow)<wfate:
                nrow.append(None)
            self.data[i] = nrow
        self.width = wfate
        return True

    def isSimilar(self,alt):
        if alt.width!=self.width:
            return False
        if alt.height!=self.height:
            return False
        for c in hxrange(self.width):
            for r in hxrange(self.height):
                v1 = "" + hxunicode(self.getCell(c,r))
                v2 = "" + hxunicode(alt.getCell(c,r))
                if (v1!=v2):
                    print("MISMATCH "+ v1 + " " + v2);
                    return False
        return True

    def clone(self):
        result = PythonTableView([])
        result.resize(self.get_width(), self.get_height())
        for c in hxrange(self.width):
            for r in hxrange(self.height):
                result.setCell(c,r,self.getCell(c,r))
        return result

    def create(self):
        return PythonTableView([])

    def getMeta(self):
        return None
for name in dir(Coopy):
    if name[0] != '_':
        vars()[name] = getattr(Coopy, name)
import sqlite3

class SqliteDatabase(SqlDatabase):
    def __init__(self,db,fname):
        self.db = db
        db.isolation_level = None
        self.fname = fname
        self.cursor = db.cursor()
        self.row = None

    # needed because pragmas do not support bound parameters
    def getQuotedColumnName(self,name):
        return name  # adequate for test, not real life

    # needed because pragmas do not support bound parameters
    def getQuotedTableName(self,name):
        return name.toString()  # adequate for test, not real life

    def getColumns(self,name):
        qname = self.getQuotedTableName(name)
        info = self.cursor.execute("pragma table_info(%s)"%qname).fetchall()
        columns = []
        for row in info:
            column = SqlColumn()
            column.setName(row[1])
            column.setPrimaryKey(row[5]>0)
            column.setType(row[2],'sqlite')
            columns.append(column)
        return columns

    def begin(self,query,args=[],order=[]):
        self.cursor.execute(query,args or [])
        return True

    def beginRow(self,tab,row,order=[]):
        self.cursor.execute("SELECT * FROM " + self.getQuotedTableName(tab) + " WHERE rowid = ?",[row])
        return True

    def read(self):
        self.row = self.cursor.fetchone()
        return self.row!=None

    def get(self,index):
        v = self.row[index]
        if v is None:
            return v
        return v

    def end(self):
        pass

    def rowid(self):
        return "rowid"

    def getHelper(self):
        return SqliteHelper()
    
    def getNameForAttachment(self):
        return self.fname
if __name__ == '__main__':
	Coopy.main()
