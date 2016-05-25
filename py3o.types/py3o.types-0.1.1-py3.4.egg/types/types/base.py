# -*- encoding: utf-8 -*-


class Py3oTypeMixin(object):
    """Base mixin for Py3o types.

    This mixin implements the methods that allows a class to be subclassed by
    a :class:`.Py3oTypeConfig` instance according to its configuration values.

    New types will typically inherit from it as well as a builtin or standard
    class.
    """

    @classmethod
    def get_type_for_config(cls, config):
        """Create a subclass with attributes extracted from the configuration.

        The keys and values returned by the base class' implementation of the
        :meth:`~Py3oTypeMixin.get_config_attributes` method will be available
        as class attributes in the new subclass.

        :param Py3oTypeConfig config: The configuration to use.
        :returns: The configured subclass for the original type.
        :rtype: type
        """
        return type(cls.__name__, (cls,), cls.get_config_attributes(config))

    @classmethod
    def get_config_attributes(cls, config):
        """Extract the relevant values from the configuration.

        :param Py3oTypeConfig config: The configuration to use.
        :returns: The attributes to add to the class' namespace.
        :rtype: dict
        """
        return {}

    @property
    def odt_value(self):  # pragma: no cover
        """The raw ODT value for the object."""
        return self
