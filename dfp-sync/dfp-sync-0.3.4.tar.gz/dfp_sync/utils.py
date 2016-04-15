import re
import cStringIO
from traceback import format_exc 
from datetime import datetime 

import fastavro
from smart_open import smart_open
from joblib import Parallel, delayed

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


def threaded(fx, items, **kw):
  """
  Run a function in parallel via joblib.
  """
  nj = kw.pop('n_jobs', 4)
  bk = kw.pop('backend', 'threading')
  return Parallel(n_jobs=nj, backend=bk)(delayed(fx)(i, **kw) for i in items)

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
    print("\n ERROR parsing:\n ")
    print(schema)
    raise ValueError(format_exc())

def parse_gcloud_config(config):
  """
  GoogleCredentials.to_json() includes some unwanted fields.
  """
  _bad_keys = ['scopes', 'token_info_uri', 'invalid', 'token_response', 'id_token']
  for k in config.keys():
    if k.startswith('_') or k in _bad_keys: 
      config.pop(k)
  return config

def parse_transfer_filepath(fp):
  """
  Parse elements of a transfer file filepath.
  """
  fp_keys = ['event_name', 'network_id', 'year', 'month', 'day', 'hour'] 
  m = _dtf_regex.match(fp)
  d = dict(zip(fp_keys, m.groups()))
  d['event_type'] = 'impression' if 'impression' in fp.lower() else 'click'
  d['backfill'] = True if 'backfill' in fp.lower() else False
  d['gcs_file'] = fp
  d['datetime'] = datetime(
    year = int(d['year']),
    month = int(d['month']),
    day = int(d['day']),
    hour = int(d['hour']),
    minute = 0,
    second = 0)
  d['fp'] = fp
  return d
