#!/usr/bin/env python
"""The EE Python library."""


__version__ = '0.1.79'

# Using lowercase function naming to match the JavaScript names.
# pylint: disable=g-bad-name

import datetime
import inspect
import json
import numbers
import os
import sys

import oauth2client.client  # pylint: disable=g-bad-import-order

from apifunction import ApiFunction
import batch
from collection import Collection
from computedobject import ComputedObject
from customfunction import CustomFunction
import data
import deserializer
from dictionary import Dictionary
from ee_date import Date
from ee_exception import EEException
from ee_list import List
from ee_number import Number
from ee_string import String
import ee_types as types
from element import Element
from encodable import Encodable
from feature import Feature
from featurecollection import FeatureCollection
from filter import Filter
from function import Function
from geometry import Geometry
from image import Image
from imagecollection import ImageCollection
from oauthinfo import OAuthInfo
from serializer import Serializer
from terrain import Terrain

# A list of autogenerated class names added by _InitializeGenerateClasses.
_generatedClasses = []


# A lightweight class that is used as a dictionary with dot notation.
class _AlgorithmsContainer(dict):

  def __getattr__(self, name):
    return self[name]

  def __setattr__(self, name, value):
    self[name] = value

  def __delattr__(self, name):
    del self[name]

# A dictionary of algorithms that are not bound to a specific class.
Algorithms = _AlgorithmsContainer()


def Initialize(credentials='persistent', opt_url=None):
  """Initialize the EE library.

  If this hasn't been called by the time any object constructor is used,
  it will be called then.  If this is called a second time with a different
  URL, this doesn't do an un-initialization of e.g.: the previously loaded
  Algorithms, but will overwrite them and let point at alternate servers.

  Args:
    credentials: OAuth2 credentials.  'persistent' (default) means use
        credentials already stored in the filesystem, or raise an explanatory
        exception guiding the user to create those credentials.
    opt_url: The base url for the EarthEngine REST API to connect to.
  """
  if credentials == 'persistent':
    credentials = _GetPersistentCredentials()
  data.initialize(credentials, (opt_url + '/api' if opt_url else None), opt_url)
  # Initialize the dynamically loaded functions on the objects that want them.
  ApiFunction.initialize()
  Element.initialize()
  Image.initialize()
  Feature.initialize()
  Collection.initialize()
  ImageCollection.initialize()
  FeatureCollection.initialize()
  Filter.initialize()
  Geometry.initialize()
  List.initialize()
  Number.initialize()
  String.initialize()
  Date.initialize()
  Dictionary.initialize()
  Terrain.initialize()
  _InitializeGeneratedClasses()
  _InitializeUnboundMethods()


def Reset():
  """Reset the library. Useful for re-initializing to a different server."""
  data.reset()
  ApiFunction.reset()
  Element.reset()
  Image.reset()
  Feature.reset()
  Collection.reset()
  ImageCollection.reset()
  FeatureCollection.reset()
  Filter.reset()
  Geometry.reset()
  List.reset()
  Number.reset()
  String.reset()
  Date.reset()
  Dictionary.reset()
  Terrain.reset()
  _ResetGeneratedClasses()
  global Algorithms
  Algorithms = _AlgorithmsContainer()


def _GetPersistentCredentials():
  """Read persistent credentials from ~/.config/earthengine.

  Raises EEException with helpful explanation if credentials don't exist.

  Returns:
    OAuth2Credentials built from persistently stored refresh_token
  """
  try:
    tokens = json.load(open(OAuthInfo.credentials_path()))
    refresh_token = tokens['refresh_token']
    return oauth2client.client.OAuth2Credentials(
        None, OAuthInfo.CLIENT_ID, OAuthInfo.CLIENT_SECRET, refresh_token,
        None, 'https://accounts.google.com/o/oauth2/token', None)
  except IOError:
    script = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'authenticate.py')
    raise EEException('Please authorize access to your Earth Engine account ' +
                      'by running\n\npython %s\n\nand then retry.' % script)


def _ResetGeneratedClasses():
  """Remove the dynamic classes."""
  global _generatedClasses

  for name in _generatedClasses:
    ApiFunction.clearApi(globals()[name])
    del globals()[name]
  _generatedClasses = []
  # Warning: we're passing all of globals() into registerClasses.
  # This is a) pass by reference, and b) a lot more stuff.
  types._registerClasses(globals())     # pylint: disable=protected-access


def ServiceAccountCredentials(email, key_file=None, key_data=None):
  """Configure OAuth2 credentials for a Google Service Account.

  Args:
    email: The email address of the account for which to configure credentials.
    key_file: The path to a file containing the private key associated with
        the service account.
    key_data: Raw key data to use, if key_file is not specified.

  Returns:
    An OAuth2 credentials object.
  """
  if key_file:
    key_data = open(key_file, 'rb').read()
  return oauth2client.client.SignedJwtAssertionCredentials(
      email, key_data, OAuthInfo.SCOPE)


def call(func, *args, **kwargs):
  """Invoke the given algorithm with the specified args.

  Args:
    func: The function to call. Either an ee.Function object or the name of
        an API function.
    *args: The positional arguments to pass to the function.
    **kwargs: The named arguments to pass to the function.

  Returns:
    A ComputedObject representing the called function. If the signature
    specifies a recognized return type, the returned value will be cast
    to that type.
  """
  if isinstance(func, basestring):
    func = ApiFunction.lookup(func)
  return func.call(*args, **kwargs)


def apply(func, named_args):  # pylint: disable=redefined-builtin
  """Call a function with a dictionary of named arguments.

  Args:
    func: The function to call. Either an ee.Function object or the name of
        an API function.
    named_args: A dictionary of arguments to the function.

  Returns:
    A ComputedObject representing the called function. If the signature
    specifies a recognized return type, the returned value will be cast
    to that type.
  """
  if isinstance(func, basestring):
    func = ApiFunction.lookup(func)
  return func.apply(named_args)


def _Promote(arg, klass):
  """Wrap an argument in an object of the specified class.

  This is used to e.g.: promote numbers or strings to Images and arrays
  to Collections.

  Args:
    arg: The object to promote.
    klass: The expected type.

  Returns:
    The argument promoted if the class is recognized, otherwise the
    original argument.
  """
  if arg is None:
    return arg

  if klass == 'Image':
    return Image(arg)
  elif klass == 'Feature':
    if isinstance(arg, Collection):
      # TODO(user): Decide whether we want to leave this in. It can be
      #              quite dangerous on large collections.
      return ApiFunction.call_(
          'Feature', ApiFunction.call_('Collection.geometry', arg))
    else:
      return Feature(arg)
  elif klass == 'Element':
    if isinstance(arg, Element):
      # Already an Element.
      return arg
    elif isinstance(arg, Geometry):
      # Geometries get promoted to Features.
      return Feature(arg)
    elif isinstance(arg, ComputedObject):
      # Try a cast.
      return Element(arg.func, arg.args, arg.varName)
    else:
      # No way to convert.
      raise EEException('Cannot convert %s to Element.' % arg)
  elif klass == 'Geometry':
    if isinstance(arg, Collection):
      return ApiFunction.call_('Collection.geometry', arg)
    else:
      return Geometry(arg)
  elif klass in ('FeatureCollection', 'Collection'):
    # For now Collection is synonymous with FeatureCollection.
    if isinstance(arg, Collection):
      return arg
    else:
      return FeatureCollection(arg)
  elif klass == 'ImageCollection':
    return ImageCollection(arg)
  elif klass == 'Filter':
    return Filter(arg)
  elif klass == 'Algorithm':
    if isinstance(arg, basestring):
      # An API function name.
      return ApiFunction.lookup(arg)
    elif callable(arg):
      # A native function that needs to be wrapped.
      args_count = len(inspect.getargspec(arg).args)
      return CustomFunction.create(arg, 'Object', ['Object'] * args_count)
    elif isinstance(arg, Encodable):
      # An ee.Function or a computed function like the return value of
      # Image.parseExpression().
      return arg
    else:
      raise EEException('Argument is not a function: %s' % arg)
  elif klass == 'Dictionary':
    if isinstance(arg, dict):
      return arg
    else:
      return Dictionary(arg)
  elif klass == 'String':
    if (types.isString(arg) or
        isinstance(arg, ComputedObject) or
        isinstance(arg, String)):
      return String(arg)
    else:
      return arg
  elif klass == 'List':
    return List(arg)
  elif klass in ('Number', 'Float', 'Long', 'Integer', 'Short', 'Byte'):
    return Number(arg)
  elif klass in globals():
    cls = globals()[klass]
    ctor = ApiFunction.lookupInternal(klass)
    # Handle dynamically created classes.
    if isinstance(arg, cls):
      # Return unchanged.
      return arg
    elif ctor:
      # The client-side constructor will call the server-side constructor.
      return cls(arg)
    elif isinstance(arg, basestring):
      if hasattr(cls, arg):
        # arg is the name of a method in klass.
        return getattr(cls, arg)()
      else:
        raise EEException('Unknown algorithm: %s.%s' % (klass, arg))
    else:
      # Client-side cast.
      return cls(arg)
  else:
    return arg


def _InitializeUnboundMethods():
  # Sort the items by length, so parents get created before children.
  items = ApiFunction.unboundFunctions().items()
  items.sort(key=lambda x: len(x[0]))

  for name, func in items:
    signature = func.getSignature()
    if signature.get('hidden', False):
      continue

    # Create nested objects as needed.
    name_parts = name.split('.')
    target = Algorithms
    while len(name_parts) > 1:
      first = name_parts[0]
      if not hasattr(target, first):
        setattr(target, first, _AlgorithmsContainer())
      target = getattr(target, first)
      name_parts = name_parts[1:]

    # Attach the function.
    # We need a copy of the function to attach properties.
    def GenerateFunction(f):
      return lambda *args, **kwargs: f.call(*args, **kwargs)  # pylint: disable=unnecessary-lambda
    bound = GenerateFunction(func)
    bound.signature = signature
    bound.__doc__ = str(func)
    setattr(target, name_parts[0], bound)


def _InitializeGeneratedClasses():
  """Generate classes for extra types that appear in the web API."""
  signatures = ApiFunction.allSignatures()
  # Collect the first part of all function names.
  names = set([name.split('.')[0] for name in signatures])
  # Collect the return types of all functions.
  returns = set([signatures[sig]['returns'] for sig in signatures])

  want = [name for name in names.intersection(returns) if name not in globals()]

  for name in want:
    globals()[name] = _MakeClass(name)
    _generatedClasses.append(name)
    ApiFunction._bound_signatures.add(name)  # pylint: disable=protected-access

  # Warning: we're passing all of globals() into registerClasses.
  # This is a) pass by reference, and b) a lot more stuff.
  types._registerClasses(globals())     # pylint: disable=protected-access


def _MakeClass(name):
  """Generates a dynamic API class for a given name."""

  def init(self, *args):
    """Initializer for dynamically created classes.

    Args:
      self: The instance of this class.  Listed to make the linter hush.
      *args: Either a ComputedObject to be promoted to this type, or
             arguments to an algorithm with the same name as this class.

    Returns:
      The new class.
    """
    klass = globals()[name]
    onlyOneArg = (len(args) == 1)
    # Are we trying to cast something that's already of the right class?
    if onlyOneArg and isinstance(args[0], klass):
      result = args[0]
    else:
      # Decide whether to call a server-side constructor or just do a
      # client-side cast.
      ctor = ApiFunction.lookupInternal(name)
      firstArgIsPrimitive = not isinstance(args[0], ComputedObject)
      shouldUseConstructor = False
      if ctor:
        if not onlyOneArg:
          # Can't client-cast multiple arguments.
          shouldUseConstructor = True
        elif firstArgIsPrimitive:
          # Can't cast a primitive.
          shouldUseConstructor = True
        elif args[0].func != ctor:
          # We haven't already called the constructor on this object.
          shouldUseConstructor = True

    # Apply our decision.
    if shouldUseConstructor:
      # Call ctor manually to avoid having promote() called on the output.
      ComputedObject.__init__(self, ctor, ctor.promoteArgs(ctor.nameArgs(args)))
    else:
      # Just cast and hope for the best.
      if not onlyOneArg:
        # We don't know what to do with multiple args.
        raise EEException(
            'Too many arguments for ee.%s(): %s' % (name, args))
      elif firstArgIsPrimitive:
        # Can't cast a primitive.
        raise EEException(
            'Invalid argument for ee.%s(): %s.  Must be a ComputedObject.' %
            (name, args))
      else:
        result = args[0]
      ComputedObject.__init__(self, result.func, result.args, result.varName)

  properties = {'__init__': init, 'name': lambda self: name}
  new_class = type(str(name), (ComputedObject,), properties)
  ApiFunction.importApi(new_class, name, name)
  return new_class


# Set up type promotion rules as soon the package is loaded.
Function._registerPromoter(_Promote)   # pylint: disable=protected-access
