import argparse
import json 

import yaml 

from transpose import schema
from transpose import converters

CONVERTERS = {
  'dict': converters.Converter(),
  'json': converters.JsonConverter(),
  'yaml': converters.YamlConverter(),
  'avro': converters.AvroConverter(),
  'avsc': converters.AvscConverter(),
  'elastic': converters.ElasticSearchConverter(),
  'elastic-json': converters.ElasticSearchJsonConverter(),
  'elastic-yaml': converters.ElasticSearchYamlConverter()
}

def new(**kw):
  """
  initialize a new schema.
  """
  kw.setdefault('converters', CONVERTERS)
  return schema.Schema(**kw)

def cli():
  """
  Command-line interface for converting between schema formats.
  """
  parser = argparse.ArgumentParser('transpose')
  parser.add_argument('schema', type=str, 
    help='The path to the schema file you want to convert.')
  parser.add_argument('--to', type=str, 
    choices=['json', 'yaml', 'avsc', 'elastic-yaml', 'elastic-json'],
    default='json',
    help='the format to convert the schemafile into')
  opts = parser.parse_args()

  with open(opts.schema, 'rb') as f:
    contents = f.read()

  if opts.schema.endswith('ml'):
    schema = yaml.load(contents)

  elif opts.schema.endswith('json'):
    schema = json.loads(contents)

  else:
    raise ValueError('Invalid schemafile: "{}". Must be yaml or json')

  schema = new(title=schema.get('title'), body=schema)
  schema.check()
  print schema.to(opts.to)

