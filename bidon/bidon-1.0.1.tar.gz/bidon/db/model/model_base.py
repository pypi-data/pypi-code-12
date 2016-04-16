"""The model_base module contains the ModelBase class."""
from bidon.util import get_value, to_json, pick, exclude
from .validation import Validator


__all__ = ["ModelBase"]


class ModelBase(object):
  """A simple model base class allowing easy specification and creation of database backed objects.
  """
  table_name = None
  primary_key_name = "id"
  primary_key_is_auto = True
  timestamps = ("created_at", "updated_at")
  attrs = {}
  validator = Validator()
  exclude_keys_serialize = set()
  exclude_keys_sql = {"created_at", "updated_at"}
  strict_attrs = False

  def __init__(self, data_=None, **attrs_):
    """Initializes the ModelBase instance.

    :data_: can be either a dictionary, another Model, or None. The instance is initialized from it.
    :attrs: are passed to the instance's update method after the instance is initialized from data_.
    """
    self._initialize_attributes(data_ or {})
    self.update(attrs_)
    self.errors = {}

  @classmethod
  def create_model_class(cls, name, table_name, attrs, validations=None, *, otherattrs=None,
                         other_bases=None):
    """Creates a new class derived from ModelBase."""
    members = dict(table_name=table_name, attrs=attrs, validations=validations or [])
    if otherattrs:
      members.update(otherattrs)
    return type(name, other_bases or (), members)

  @classmethod
  def has_attr(cls, attr_name):
    """Check to see if an attribute is defined for the model."""
    if attr_name in cls.attrs:
      return True

    if isinstance(cls.primary_key_name, str) and cls.primary_key_name == attr_name:
      return True

    if isinstance(cls.primary_key_name, tuple) and attr_name in cls.primary_key_name:
      return True

    if cls.timestamps is not None and attr_name in cls.timestamps:
      return True

    return False

  @property
  def primary_key(self):
    """Returns either the primary key value, or a tuple containing the primary key values in the
    case of a composite primary key.
    """
    pkname = self.primary_key_name
    if pkname is None:
      return None
    elif isinstance(pkname, str):
      return getattr(self, pkname)
    else:
      return tuple((getattr(self, pkn) for pkn in pkname))

  @property
  def is_new(self):
    """Determines whether or not a model has been saved to the database or not by checking its
    primary key value.
    """
    if not self.primary_key_is_auto:
      raise Exception("Unable to determine newness of non-auto increment primary key moodels")
    return self.primary_key is None

  def before_validation(self):
    """Method to call before validation is run. Allows subclasses to fixup their properties."""
    pass

  def validate(self, data_access=None):
    """Run the class validations against the instance. If the validations require database access,
    pass in a DataAccess derived instance.
    """
    self.clear_errors()
    self.before_validation()
    self.validator.validate(self, data_access)
    return not self.has_errors

  @property
  def has_errors(self):
    """Returns True if there are any errors recorded for the instance."""
    return bool(self.errors)

  def add_error(self, property_name, message):
    """Add an error for the given property."""
    if property_name not in self.errors:
      self.errors[property_name] = []
    self.errors[property_name].append(message)

  def clear_errors(self):
    """Clears all errors."""
    self.errors.clear()

  def all_errors(self, joiner="; "):
    """Returns a string representation of all errors recorded for the instance."""
    parts = []
    for pname, errs in self.errors.items():
      for err in errs:
        parts.append("{0}: {1}".format(pname, err))
    return joiner.join(parts)

  def to_dict(self, *, include_keys=None, exclude_keys=None, use_default_excludes=True):
    """Converts the class to a dictionary.

    :include_keys: if not None, only the attrs given will be included.
    :exclude_keys: if not None, all attrs except those listed will be included, with respect to
    use_default_excludes.
    :use_default_excludes: if True, then the class-level exclude_keys_serialize will be combined
    with exclude_keys if given, or used in place of exlcude_keys if not given.
    """
    data = self.__dict__

    if include_keys:
      return pick(data, include_keys, transform=self._other_to_dict)
    else:
      skeys = self.exclude_keys_serialize if use_default_excludes else None
      ekeys = exclude_keys

      return exclude(
        data,
        lambda k: (skeys is not None and k in skeys) or (ekeys is not None and k in ekeys),
        transform=self._other_to_dict)

  def to_json(self, *, include_keys=None, exclude_keys=None, use_default_excludes=True,
              pretty=False):
    """Converts the response from to_dict to a JSON string. If pretty is True then newlines,
    indentation and key sorting are used.
    """
    return to_json(
      self.to_dict(
        include_keys=include_keys,
        exclude_keys=exclude_keys,
        use_default_excludes=use_default_excludes),
      pretty=pretty)

  def update(self, data_=None, **kwargs):
    """Update the object with the given data object, and with any other key-value args. Returns a
    set containing all the property names that were changed.
    """
    if data_ is None:
      data_ = dict()
    else:
      data_ = dict(data_)
    data_.update(**kwargs)
    changes = set()
    for attr_name in data_:
      if hasattr(self, attr_name):
        if getattr(self, attr_name) != data_[attr_name]:
          changes.add(attr_name)
          setattr(self, attr_name, data_[attr_name])
      else:
        if self.strict_attrs:
          raise Exception("Unknown attribute for {}: {}".format(self.__class__.__name__, attr_name))
    return changes

  def _initialize_attributes(self, data):
    """Initializes the class with the given data. Used by __init__."""
    attrs = dict(self.attrs)

    if self.primary_key_name is None:
      pass
    elif isinstance(self.primary_key_name, str):
      if self.primary_key_name not in attrs:
        attrs[self.primary_key_name] = None
    else:
      for pkey in self.primary_key_name:
        if pkey not in attrs:
          attrs[pkey] = None

    if self.timestamps:
      for ts_name in self.timestamps:
        if ts_name is not None and ts_name not in attrs:
          attrs[ts_name] = None

    for attr_name in attrs:
      setattr(self, attr_name, get_value(data, attr_name, attrs[attr_name]))

  def _other_to_dict(self, other):
    """When serializing models, this allows attached models (children, parents, etc.) to also be
    serialized.
    """
    if isinstance(other, ModelBase):
      return other.to_dict()
    elif isinstance(other, list):
      # TODO: what if it's not a list?
      return [self._other_to_dict(i) for i in other]
    else:
      return other
