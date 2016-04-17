"""The configuration module contains the Configuration class."""

class Configuration(object):
  """A freezable configuration object. Instances of this class can be constructed and updated and
  finally frozen to prevent new values from being added, or existing values from being edited.
  """
  def __init__(self, **kwargs):
    """Initializes the Configuration class. Each parameter becomes a property on the instance."""
    self._frozen_ = False
    self.update(**kwargs)

  @property
  def is_frozen(self):
    """Returns True if the instance is frozen, preventing properties from being added or edited."""
    return hasattr(self, "_frozen_") and self._frozen_

  def update(self, **kwargs):
    """Creates or updates a property for the instance for each parameter."""
    for key, value in kwargs.items():
      setattr(self, key, value)

  def freeze(self):
    """Freezes the instance, preventing new attributes from being added or edited."""
    if not self.is_frozen:
      self._frozen_ = True

  def __setattr__(self, k, v):
    """Overrides setattr to enforze the frozen attribute."""
    if self.is_frozen:
      raise Exception("Configuration is frozen")
    super().__setattr__(k, v)
