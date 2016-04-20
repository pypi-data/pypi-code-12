import re
import cStringIO
from traceback import format_exc 
from datetime import datetime 

import fastavro
from smart_open import smart_open

# camel case => underscore
_re_cml1 = re.compile('(.)([A-Z][a-z]+)')
_re_cml2 = re.compile('([a-z0-9])([A-Z])')

# data transfer file regex.
_dtf_regex = re.compile(r'([A-Z][^_]+)_([0-9]+)_([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2}).gz')


def no_camel(s):
  """
  parse camel case to underscore. fight me
  """
  # parse camel case
  s1 = _re_cml1.sub(r'\1_\2', s).replace('-', '_')
  return  _re_cml2.sub( r'\1_\2', s1).lower()


def obj_to_avro(records, schema):
  """
  Convert records to avro
  """
  out = cStringIO.StringIO()
  fastavro.writer(out, schema, records)
  return out.getvalue()

def write_to_s3(fp, contents, key=None, secret=None):
  """
  Write contents to s3.
  """
  if any([key, secret]):
    if not all([key, secret]):
      raise ValueError('Authenticated requests to s3 require "key" and "secret" keyword arguments.')
    fp = fp.replace('s3://', 's3://{}:{}@'.format(key, secret))
  with smart_open(fp, 'wb') as f:
    f.write(contents)

def write_avro_to_s3(fp, records, schema, key=None, secret=None):
  """
  Write avro to s3.
  """
  try:
    avro = obj_to_avro(records, schema)
    write_to_s3(fp, avro, key, secret)
  except Exception as e:
    raise ValueError(format_exc())
