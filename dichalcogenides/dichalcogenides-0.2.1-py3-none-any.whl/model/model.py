import os

from . import Material
from . import System

class Model:
    """Combines material properties with system parameters.

    If, on instantiation, ``model`` or ``system`` is a string,
    the associated object will be created from the YAML file, e.g.,

    .. code-block:: python

       Model('mos2', 'default', 'data')

    will load the YAML files at ``data/mos2.yml`` and ``data/default.yml``.
    See :meth:`parameters.Parameters.load_file`.
    """

    def __init__(self, material=Material(), system=System(), root=''):
        if isinstance(material, str):
            self.material = Material(
                os.path.join(root, 'materials', material) + '.yml')
        else: self.material = material

        if isinstance(system, str):
            self.system = System(
                os.path.join(root, 'systems', system) + '.yml')
        else: self.system = system

    @property
    def material(self):
        """The associated :class:`.Material` object.

        :return: The material.
        :rtype: Material
        """
        return self._material

    @material.setter
    def material(self, value):
        self._material = value

    @property
    def system(self):
        """The associated :class:`.System` object.

        :return: The system.
        :rtype: System
        """
        return self._system

    @system.setter
    def system(self, value):
        self._system = value

    def material_parameter(self, name):
        """Get the value of a material parameter by name.

        :param name: Material name.
        :type name: str

        :return: The value.
        :rtype: float
        """
        return self.material.get_value(name)

    def system_parameter(self, name):
        """Get the value of a system parameter by name.

        :param name: System name.
        :type name: str

        :return: The value.
        :rtype: float
        """
        return self.system.get_value(name)
