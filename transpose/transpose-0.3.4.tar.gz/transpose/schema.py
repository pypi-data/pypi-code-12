import re
import copy
import hashlib
import json
import datetime
from traceback import format_exc
from operator import itemgetter

from jsonschema import validate
from jsonschema import Draft4Validator

# camel case => underscore
_re_cml1 = re.compile('(.)([A-Z][a-z]+)')
_re_cml2 = re.compile('([a-z0-9])([A-Z])')

def no_camel(s):
  # parse camel case
  s1 = _re_cml1.sub(r'\1_\2', s)\
    .strip()\
    .replace('-', '_')\
    .replace(' ', '_')
  return  _re_cml2.sub( r'\1_\2', s1).lower()


class SchemaError(Exception):
  """
  Raised when a schema is invalid.
  """
  pass


class Schema:
  """
  An intelligently updating schema store.
  Records are stored as JSON-SCHEMA and 
  converted to other formats via 
  standard customizable methods.
  """
  
  # lookup of common python types to their
  # jsonschema equivalent
  TYPE_MAP = [
    (bool, "boolean"),
    (int, "integer"),
    (long, "integer"),
    (float, "number"),
    (unicode, "string"),
    (str, "string"),
    (datetime.datetime, "date-time")
  ]

  BASE = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": '',
    "description":  '',
    "type": "object",
    "properties": {}
  }

  BASE_OBJECT = {
    "type": "object",
    "properties": {}
  }

  

  def __init__(self, **kw):
    """
    initialize json schema
    """
    body = copy.copy(self.BASE)
    self.body = self._update_schema(body, kw.get('body', {}))
    # include title and description
    self.body['title'] = no_camel(kw.get('title', ''))
    self.converters = kw.get('converters')
    for k in ['description']:
      self.body[k] = kw.get(k, '')
    if not self.body['title']:
      raise SchemaError('A schema requires a title')
    self.types = TypeCounter()

  @property
  def md5(self):
    """
    md5 of schema object.
    """
    return hashlib.md5(self.to('json', indent=None)).hexdigest()

  def to(self, format="json", **kw):
    """
    Convert this schema to another format.
    """
    if format not in self.converters:
      raise ValueError("{0} is not a valid export format. Choose from:\n{1}".format(format, ", ".join(self.converters.keys())))
    s = self.converters.get(format)
    return s.to(self, **kw)

  def check(self):
    """
    Check if our schema is valid.
    """
    try:
      Draft4Validator.check_schema(self.body)
    except Exception as e:
      raise SchemaError(format_exc())
    return True

  def clear(self):
    """
    Clear our schema.
    """
    body = copy.copy(self.BASE)
    self.body = body
    return True

  def update(self, obj, **kw):
    """
    Initialize json schema on an object.
    """
    try:
      p = self._map_json_schema_properties(obj, **kw)
      p2 = self._update_schema(self.body['properties'], p, **kw)
      self.body['properties'] = p2
    except Exception as e:
      raise SchemaError("{0}: {1}".format(self.body['title'], format_exc()))

  def validate(self, obj):
    """
    Validate an object against this schema
    """
    try:
      validate(obj, self.body)
    except Exception as e:
      raise SchemaError(format_exc())
    return True

  def _update_schema(self, d, u, **kw):
    """
    Recursively update a nested schema.
    Modified from: 
    http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    kw.setdefault('overwrite', False)
    for k, v in u.iteritems():
      
      if isinstance(v, dict):
        d[k] = self._update_schema(d.get(k, {}), v, **kw)
      
      elif isinstance(v, list):
        vv = d.get(k, [])
        if not isinstance(vv, list):
          vv = [vv] 
        d[k] = vv + v 
        if not isinstance(v[0], dict):
          d[k] = list(set(d[k]))

      else:
        # only add it if it doesn't already exist
        if not kw.get('overwrite'):
          if not d.get(k):
            d[k] = u[k]
        else:
            d[k] = u[k]
    return d

  def _map_json_schema_properties(self, obj, pk="", **kw):
    """
    Recursively generate a json schema 
    from a dictionary of python objects.
    """
    properties = {}
    for k,v in obj.iteritems():
      uniq_k = ".".join([pk, k])

      if not k in properties:
        properties[k] = {}
      
      # recurse on dictionaries
      if isinstance(v, dict):
       
        properties[k] = copy.copy(self.BASE_OBJECT)
        p = self._map_json_schema_properties(v, uniq_k)
        properties[k]['properties'] = p
      
      # generate arrays
      elif isinstance(v, list):
        properties[k] = {'type': 'array'}
      
        # .. of dicts
        if isinstance(v[0], dict):
          properties[k]['items'] = copy.copy(self.BASE_OBJECT)
          for vv in v:
            p = self._map_json_schema_properties(vv, uniq_k)
            properties[k]['items']['properties'] = p
        
        # .. of simple types
        else:
          # simple items:
          properties[k]['items'] = {
            'type': self._map_json_schema_type(uniq_k, v[0], **kw)
          }

      # handle simple types.
      else:
        properties[k] = {
          'type': self._map_json_schema_type(uniq_k, v, **kw)
        }

    return properties

  def _map_json_schema_type(self, key, val, **kw):
    """
    Map a simple python type to json schema type.
    """
    nullable = kw.setdefault('nullable', True)
    m = kw.setdefault('default_type', ['null'])
    for typ, mapping in self.TYPE_MAP:
      if isinstance(val, typ):
        m = mapping 
        break

    # increment this type
    self.types.incr(key, m)

    # get all types so far
    m = self.types.get(key)

    # make all simple types nullable
    if nullable and m[0] != "null":
      m = ['null'] + m

    return m


class TypeCounter:
  """
  A special class for keeping track of schema types.
  """
  
  def __init__(self):
    self.types = {}

  def incr(self, k, v):
    """
    Increment a type
    """
    # ignore nulls
    if v == "null":
      return
    if not isinstance(v, list):
      v = [v]
    
    # init
    if k not in self.types:
      self.types[k] = {}
    
    # loop through values
    for vv in v:
      
      # ignore nulls
      if vv == "null": continue

      # init counter
      if vv not in self.types[k]:
        self.types[k][vv] = 0

      # increment
      self.types[k][vv] += 1

    return

  def get(self, k):
    """
    Get the most probablistic type for this key.
    """
    d = self.types.get(k)
    if not len(d.keys()):
      return ["null"]
    return sorted(d, key=itemgetter(1))
