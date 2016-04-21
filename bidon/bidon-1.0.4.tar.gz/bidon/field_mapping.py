"""Contains the FieldMapping class."""
from collections import namedtuple

from bidon.util import has_value
from bidon.util.convert import identity


class FieldMapping(object):
  """This class contains a definition for mapping a field in a structure to a new structure,
  potentially changing its name and value.
  """
  def __init__(self, source_name, destination_name=None, convert=None, is_required=True):
    """Initialize the FieldMapping instance."""
    self.source_name = source_name
    self.destination_name = destination_name or source_name
    self.convert = convert or identity
    self.is_required = is_required

  def get_value(self, source):
    """Apply self.convert to the source. The parameter passed to convert depends on
    self.source_name. If source_name is given, self.convert(getattr(source, source_name)) is called,
    otherwise self.convert(source) is called.
    """
    if self.source_name is None:
      present, value = True, self.convert(source)
      converted = True
    else:
      present, value = has_value(source, self.source_name)
      converted = False

    if not present or value is None:
      if self.is_required:
        raise ValueError("required value not present")
      else:
        return None
    else:
      if converted:
        return value
      else:
        return self.convert(value)

  @classmethod
  def get_namedtuple(cls, field_mappings, name="Record"):
    """Gets a namedtuple class that matches the destination_names in the list of field_mappings."""
    return namedtuple(name, [fm.destination_name for fm in field_mappings])

  @classmethod
  def get_namedtuple_factory(cls, field_mappings, name="Record"):
    """Gets a method that will convert a dictionary to a namedtuple, as defined by
    get_namedtuple(field_mappings).
    """
    ntup = cls.get_namedtuple(field_mappings, name)
    return lambda data: ntup(**data)

  @classmethod
  def transfer(cls, field_mappings, source, destination_factory):
    """Convert a record to a dictionary via field_mappings, and pass that to destination_factory."""
    data = dict()
    for index, field_mapping in enumerate(field_mappings):
      try:
        data[field_mapping.destination_name] = field_mapping.get_value(source)
      except Exception as ex:
        raise Exception(
          "Error with mapping #{0} '{1}'->'{2}': {3}".format(
            index,
            field_mapping.source_name,
            field_mapping.destination_name, ex)) from ex
    return destination_factory(data)

  @classmethod
  def transfer_all(cls, field_mappings, sources, destination_factory=None):
    """Calls cls.transfer on all records in sources."""
    for index, source in enumerate(sources):
      try:
        yield cls.transfer(field_mappings, source, destination_factory or (lambda x: x))
      except Exception as ex:
        raise Exception("Error with source #{0}: {1}".format(index, ex)) from ex
