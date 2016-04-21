"""This module contains methods for transforming structured data, such as ElementTree nodes or
dictionaries into other types of values.

It is especially useful for turning JSON or XML data into models.
"""
import bidon.json_patch as JP
from bidon.util import flatten_dict


def get_val(source, extract=None, transform=None):
  """Extract a value from a source, transform and return it."""
  if extract is None:
    raw_value = source
  else:
    raw_value = extract(source)

  if transform is None:
    return raw_value
  else:
    return transform(raw_value)


def get_obj(source, extract=None, child_transform=None, transform=None):
  """Maps an object based on a key->extractor child_transform dict."""
  if extract is None:
    obj = source
  else:
    obj = extract(source)

  if child_transform is None:
    data = obj
  else:
    data = dict()
    for k, v in child_transform.items():
      try:
        data[k] = v(obj)
      except Exception as ex:
        raise Exception("An error occurred with child {0}".format(k)) from ex

  if transform is None:
    return data
  else:
    return transform(data)


def get_lst(source, extract=None, transform=None):
  """Extract a list from a source, transform each item, and return the result."""
  if extract is None:
    raw_list = source
  else:
    raw_list = extract(source)

  if transform is None:
    return raw_list
  else:
    tlist = []
    for idx, item in enumerate(raw_list):
      try:
        tlist.append(transform(item))
      except Exception as ex:
        raise Exception("An error occurred with item #{0}".format(idx)) from ex
    return tlist


def get_composition(source, *fxns):
  """Compose several extractors together, on a source."""
  val = source
  for fxn in fxns:
    val = fxn(val)
  return val


def get_flattened(dct, names, path_joiner="_"):
  """Flatten a child dicts, whose resulting keys are joined by path_joiner.

  E.G. { "valuation": { "currency": "USD", "amount": "100" } } ->
       { "valuation_currency": "USD", "valuation_amount": "100" }
  """
  new_dct = dict()
  for key, val in dct.items():
    if key in names:
      child = {path_joiner.join(k): v for k, v in flatten_dict(val, (key, ))}
      new_dct.update(child)
    else:
      new_dct[key] = dct[key]
  return new_dct


def get_hoisted(dct, child_name):
  """Pulls all of a child's keys up to the parent, with the names unchanged."""
  child = dct[child_name]
  del dct[child_name]
  dct.update(child)
  return dct


def val(extract=None, transform=None):
  """Returns a partial of get_val that only needs a source argument."""
  return lambda source: get_val(source, extract, transform)


def obj(extract=None, child_transform=None, transform=None):
  """Returns a partial of get_obj that only needs a source argument."""
  return lambda source: get_obj(source, extract, child_transform, transform)


def lst(extract=None, transform=None):
  """Returns a partial of get_lst that only needs a source argument."""
  return lambda source: get_lst(source, extract, transform)


def compose(*fxns):
  """Returns a partial of get_composition that only needs a source argument."""
  return lambda source: get_composition(source, *fxns)


def flatten(names, path_joiner="_"):
  """Returns a partial of get_flattened that only needs a dct argument."""
  return lambda dct: get_flattened(dct, names, path_joiner)


def hoisted(child_name):
  """Returns a partial of get_hoisted that only needs a dct argument."""
  return lambda dct: get_hoisted(dct, child_name)


def get_xml_attr(source, name, path=None):
  """Get the XML attribute with name from source. If path is not Mone, it will instead get the
  XML attribute with name from the child indicated by path.
  """
  if path is None:
    return source.attrib[name]
  else:
    return get_xml_attr(get_xml_child(source, path), name)


def get_xml_text(source, path=None):
  """Get the text of the XML node. If path is not None, it will get the text of the descendant of
  source indicated by path.
  """
  if path is None:
    return source.text
  else:
    return get_xml_text(get_xml_child(source, path))


def get_xml_child(source, path):
  """Get the first descendant of source identified by path.

  Path must be either a an xpath string, or a 2-tuple of (xpath, namespace_dict).
  """
  if isinstance(path, (tuple, list)):
    return source.find(*path)
  else:
    return source.find(path)


def get_xml_children(source, path):
  """Get all the descendants of source identified by path.

  Path must be either a an xpath string, or a 2-tuple of (xpath, namespace_dict).
  """
  if isinstance(path, (tuple, list)):
    return source.findall(*path)
  else:
    return source.findall(path)


def xml_attr(name, path=None):
  """Returns a partial of get_xml_attr that only needs a source argument."""
  return lambda source: get_xml_attr(source, name, path)


def xml_text(path=None):
  """Returns a partial of get_xml_text that only needs a source argument."""
  return lambda source: get_xml_text(source, path)


def xml_child(path):
  """Returns a partial of get_xml_child that only needs a source argument."""
  return lambda source: get_xml_child(source, path)


def xml_children(path):
  """Returns a partial of get_xml_children that only needs a source argument."""
  return lambda source: get_xml_children(source, path)


def get_json_val(source, path, *, ignore_bad_path=False):
  """Get the nested value identified by the json path, rooted at source."""
  try:
    return JP.find(source, path)
  except JP.JSONPathError as ex:
    if ignore_bad_path:
      return None
    else:
      raise


def get_json_vals(source, path):
  """Get all the nested values identified by the json path, rooted at source."""
  yield from JP.find_all(source, path)


def json_val(path, *, ignore_bad_path=False):
  """Returns a partial of get_json_val that only needs a source argument."""
  return lambda source: get_json_val(source, path, ignore_bad_path=ignore_bad_path)


def json_vals(path):
  """Returns a partial of get_json_vals that only needs a source argument."""
  return lambda source: get_json_vals(source, path)
