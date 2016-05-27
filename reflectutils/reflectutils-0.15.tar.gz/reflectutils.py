import re
import types
import inspect

# Regex for bound builtin methods
#
#    >>> str(re.compile("\w+").search)
#    <built-in method search of _sre.SRE_Pattern object at 0x105648558>
BOUND_BUILTIN_METHOD_PATTERN = re.compile(r'<built-in method (?P<name>\w+) of (?P<type>[0-9A-Za-z._]+) object at .+>')

# Regex for bound methods:
#
#    >>> str(subprocess.Popen('true')).kill)
#    <bound method Popen.kill of <subprocess.Popen object at 0x1056309d0>>
#
# The printf pattern is "<bound method %s.%s of %s>"
# https://github.com/python/cpython/blob/master/Objects/classobject.c#L270
BOUND_METHOD_PATTERN = re.compile(r'<bound method (?P<shorttype>\w+)\.(?P<name>\w+) of <(?P<type>[0-9A-Za-z._]+) (object )?at .+>>')

# Regex for unbound methods
#
#    >>> str(re.compile("\w+").__class__.search)
#    <method 'search' of '_sre.SRE_Pattern' objects>
#    >>> str(file.flush)
#    <method 'flush' of 'file' objects>
UNBOUND_METHOD_PATTERN = re.compile(r"<method '(?P<name>\w+)' of '(?P<type>[0-9A-Za-z._]+)' objects>")

# Alternative regex for unbound methods:
#
#    >>> str(subprocess.Popen.kill)
#    <unbound method Popen.kill>
UNBOUND_METHOD_PATTERN_2 = re.compile(r'<unbound method (?P<qualname>[0-9A-Za-z._]+)>')

# Regex for unbound data descriptors
#
#    >>> str(numpy.ndarray.ndim)
#    <attribute 'ndim' of 'numpy.ndarray' objects>
UNBOUND_DATA_DESCRIPTOR_PATTERN = re.compile(r"<attribute '(?P<name>\w+)' of '(?P<type>[0-9A-Za-z._]+)' objects>")


def classify(x):
	"""
	Classify x as one of five high-level types: module, function, descriptor, type, or object
	"""
	if inspect.ismodule(x):
		return "module"
	elif inspect.isroutine(x):  # isroutine returns true for any kind of function or method
		return "function"
	elif inspect.ismemberdescriptor(x) or inspect.isgetsetdescriptor(x) or inspect.isdatadescriptor(x):
		return "descriptor"
	elif inspect.isclass(x):
		return "type"
	else:
		return "object"


def fullname_from_str(s, pkg=None):
	"""
	Try to extract the fully qualified name of an object from the result of calling str()
	on the object. This is the last resort for getting the name of an object but is the
	only option for many C functions and builtins.
	"""
	# attempt to match bound builtins
	match = BOUND_BUILTIN_METHOD_PATTERN.match(s)
	if match:
		parts = match.groupdict()
		return parts["type"] + "." + parts["name"]

	# attempt to match bound methods
	match = BOUND_METHOD_PATTERN.match(s)
	if match:
		parts = match.groupdict()
		return parts["type"] + "." + parts["name"]

	# attempt to match unbound methods
	match = UNBOUND_METHOD_PATTERN.match(s)
	if match:
		parts = match.groupdict()
		typename = parts["type"]
		if not "." in typename:
			typename = "__builtin__." + typename
		return typename + "." + parts["name"]

	# attempt alternative unbound method match (only if we already have the package)
	if pkg:
		match = UNBOUND_METHOD_PATTERN_2.match(s)
		if match:
			parts = match.groupdict()
			return pkg + "." + parts["qualname"]

	# attempt to match unbound data descriptors
	match = UNBOUND_DATA_DESCRIPTOR_PATTERN.match(s)
	if match:
		parts = match.groupdict()
		typename = parts["type"]
		if not "." in typename:
			typename = "__builtin__." + typename
		return typename + "." + parts["name"]

	return None


def fullname(obj):
	"""
	Get the fully-qualified name for the given object, or empty string if no fully qualified
	name can be deduced (which is typically the case for things that are neither types nor 
	modules)
	"""
	# If we have a module then just return the name
	if inspect.ismodule(obj):
		return getattr(obj, "__name__", "")

	# Try to get the qualified name
	name = getattr(obj, "__qualname__", None)

	# Fall back to using "__name__" but only for non-methods
	if not inspect.ismethod(obj):
		name = getattr(obj, "__name__", None)

	# Look for "__objclass__" -- e.g. for "str.join" this is "str"
	owner = getattr(obj, "__objclass__", None)
	if owner is not None and owner is not obj and not inspect.ismemberdescriptor(owner):
		ownername = fullname(owner)
		if ownername is not None:
			return ownername + "." + name

	# Try to get the module
	pkg = getattr(obj, "__module__", None)
	if name is not None and pkg is not None:
		return pkg + "." + name

	# finally fall back to using str(obj) and matching against regexes
	return fullname_from_str(str(obj), pkg)


def getclass(obj):
	"""
	Unfortunately for old-style classes, type(x) returns types.InstanceType. But x.__class__
	gives us what we want.
	"""
	return getattr(obj, "__class__", type(obj))


def argspec(obj):
	"""
	Get a dictionary representing the call signature for the given function
	 "args" -> list of arguments, each one is a dict with keys "name" and "default_type"
	 "vararg" -> name of *arg, or None
	 "kwarg" -> name of **kwarg, or None
	"""
	try:
		spec = inspect.getargspec(obj)
	except TypeError:
		return None

	args = []
	for i, name in enumerate(spec.args):
		if not isinstance(name, basestring):
			# this can happen when args are declared as tuples, as in
			# def foo(a, (b, c)): ...
			name = "autoassigned_arg_%d" % i
		default_type = ""
		if spec.defaults is not None:
			idx = i - len(spec.args) + len(spec.defaults)
			if idx >= 0:
				default_type = fullname(getclass(spec.defaults[idx]))
		args.append(dict(name=name, default_type=default_type))
	return dict(
		args=args,
		vararg=spec.varargs,
		kwarg=spec.keywords)


def doc(x):
	"""
	Get the documentation for x, or empty string if there is no documentation.
	"""
	s = inspect.getdoc(x)
	if isinstance(s, basestring):
		return s
	else:
		return ""


def package(x):
	"""
	Get the package in which x was first defined, or return None if that cannot be determined.
	"""
	return getattr(x, "__package__", None) or getattr(x, "__module__", None)
