import yaml

from . import Parameter

class Parameters:
    """Collection of parameters.

    New instances may optionally be passed a ``path`` to a YAML file.
    See :meth:`.load_file`.

    .. code-block:: python

      parameters = Parameters()
      parameters.add_parameter('warp speed', 9.0)
      parameters.get_value('warp speed') #=> 9.0

      parameters.set_value('warp speed', 10.0)
      parameters.get_value('warp speed') #=> 10.0
    """

    def __init__(self, path=None):
        if path: self.load_file(path)

    @property
    def name(self):
        """The name of this parameter set.

        :return: Parameter set name.
        :rtype: str
        :default: None
        """
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def property_keys(self):
        """Keys to load as class properties when loading from file.

        :return: Key names.
        :rtype: dict
        :default: ``['name']``
        """
        if not hasattr(self, '_property_keys'):
            self._property_keys = ['name']
        return self._property_keys

    @property_keys.setter
    def property_keys(self, value):
        self._property_keys = value

    @property
    def parameters(self):
        """The list of :class:`.Parameter` objects.

        :return: Parameter list.
        :rtype: dict
        :default: ``[]``
        """
        if not hasattr(self, '_parameters'): self._parameters = []
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        self._parameters = value

    def get(self, name):
        """Get a parameter object by name.

        :param name: Name of the parameter object.
        :type name: str

        :return: The parameter.
        :rtype: Parameter
        """
        parameter = next((p for p in self.parameters if p.name == name), None)
        if parameter is None:
            raise LookupError("Cannot find parameter '" + name + "'.")
        return parameter

    def add_parameter(self, name, value, meta=None):
        """Add a parameter to the parameter list.

        :param name: New parameter's name.
        :type name: str

        :param value: New parameter's value.
        :type value: float

        :param meta: New parameter's meta property.
        :type meta: dict
        """
        parameter = Parameter(name, value)
        if meta: parameter.meta = meta
        self.parameters.append(parameter)

    def get_value(self, name):
        """Get the value of a parameter by name.

        :return: Parameter value.
        :rtype: Parameter
        """
        return self.get(name).value

    def set_value(self, name, value):
        """Set the value of a parameter by name.

        :param name: Parameter name.
        :type name: str

        :param value: Parameter value.
        :type value: float
        """
        self.get(name).value = value

    def get_meta(self, name):
        """Get the metadata of a parameter by name.

        :return: Parameter metadata.
        :rtype: dict
        """
        return self.get(name).meta

    def load_file(self, path):
        """Load a YAML file with parameter data and other metadata.

        :param path: Path to YAML file.
        :type path: str

        The data in the YAML file is used to set the properties for the instance.
        The YAML file must contain a ``parameters`` key.
        It may optionally include any keys defined in :attr:`.property_keys`.

        .. code-block:: yaml

          # data.yml
          ---
          name: Shield frequencies
          parameters:
            - name: a
              value: 24.50
            - name: β
              value: 42.10
              meta:
                phase_inverted: true


        .. code-block:: python

          parameters = Parameters('data.yml')
          parameters.name #=> 'Shield frequencies'
          parameters.get_value('a') #=> 24.50
          parameters.get_meta('β')['phase_inverted'] #=> true
        """
        data = yaml.load(open(path, 'r'))
        for key in self.property_keys:
            if key in data: setattr(self, key, data[key])
        self.parameters = self.parameter_list(data['parameters'])

    @staticmethod
    def parameter_list(data):
        """Create a list of parameter objects from a dict.

        :param data: Dictionary to convert to parameter list.
        :type data: dict

        :return: Parameter list.
        :rtype: dict
        """
        items = []
        for item in data:
            param = Parameter(item['name'], item['value'])
            if 'meta' in item: param.meta = item['meta']
            items.append(param)
        return items
