class Parameter:
    """Defines a parameter with a name and a value.

    Must provide a name and value.
    Parameters have a generic metadata property stored as a dictionary.

    .. code-block:: python

      parameter = Parameter('warp speed', 9.0, {'max': 10.0})
      parameter.name #=> 'warp speed'
      parameter.value #=> 9.0
      parameter.meta['max'] #=> 10.0
    """
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @property
    def name(self):
        """The name of this parameter.

        :return: Parameter name.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def value(self):
        """The value of this parameter.

        :return: Parameter name.
        :rtype: float
        """
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def meta(self):
        """The metadata of this parameter.

        :return: Parameter metadata.
        :rtype: dict
        :default: ``{}``
        """
        if not hasattr(self, '_meta'): self._meta = {}
        return self._meta

    @meta.setter
    def meta(self, value):
        self._meta = value
