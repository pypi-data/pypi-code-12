"""The foreign_model_wrapper module contains the ForeignModelWrapper class."""
from bidon.util.transform import get_obj
from .model_base import ModelBase


__all__ = ["ForeignModelWrapper"]


class ForeignModelWrapper(ModelBase):
  """This class is a specialization on ModelBase that can be configurued with information on how to
  transform a data structure, such a dictionary or an XML tree, to a Model.
  """
  timestamps = None
  table_name = None
  primary_key_name = None
  primary_key_is_auto = False
  transform_args = None

  @classmethod
  def create(cls, source, *, transform_args=None):
    """Create an instance of the class from the source. By default cls.transform_args is used, but
    can be overridden by passing in transform_args.
    """
    if transform_args is None:
      transform_args = cls.transform_args

    return cls(get_obj(source, *transform_args))

  @classmethod
  def map(cls, sources, *, transform_args=None):
    """Generates instances from the sources using either cls.transform_args or transform_args
    argument if present.
    """
    for idx, source in enumerate(sources):
      try:
        yield cls.create(source, transform_args=transform_args)
      except Exception as ex:
        raise Exception("An error occurred with item {0}".format(idx)) from ex

