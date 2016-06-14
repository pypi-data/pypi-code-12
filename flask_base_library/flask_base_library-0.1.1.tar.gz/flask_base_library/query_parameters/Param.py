from datetime import datetime


class Param(object):
    """The Param class defines an HTTP Query String parameter which can be a datetime, str, int, or float.
The class has attributes defining the name, type, mandatory, default value, and value of a parameter. Params
are used with fetch_parameters to retrieve query string values (e.g. http://lorem.ipsum.com/resource?param=2)
"""
    @staticmethod
    def _check_name(value= None):
        """Check the name provided is valid"""
        if value in ('', None):
            raise ValueError('Name cannot be none, blank, or empty string.')
        if not isinstance(value, str):
            raise TypeError('Name must be a string')

    @staticmethod
    def _check_type(value= None):
        """Check the type provided is valid and one of datetime, str, int, or float"""
        supported_types = [datetime, str, int, float]
        if value in ('', None):
            raise ValueError('Type cannot be none.')
        if not isinstance(value, type):
            raise TypeError('Type must be a valid type passed as a type')
        if value not in supported_types:
            raise TypeError('Type can only be one of {0}'.format(supported_types))

    @staticmethod
    def _check_required(value= None):
        """Check the required value is provided and ensure it is a bool"""
        if value in ('', None):
            raise ValueError('Required cannot be none.')
        if not isinstance(value, bool):
            raise ValueError('Parameter required must be a bool (True or False).')

    def __init__(
            self,
            p_name,
            p_type,
            p_required,
            p_default= None
    ):
        """
        The constructor takes four parameters - name, type, required, and a default.
        :param p_name:
        :param p_type:
        :param p_required:
        :param p_default:
        """
        self._check_name(p_name)
        self.p_name = p_name

        self._check_type(p_type)
        self.p_type = p_type

        self._check_required(p_required)
        self.p_required = p_required

        self.p_default = p_default
        self.value_found = None

    @property
    def parameter_name(self):
        return self.p_name

    @parameter_name.setter
    def parameter_name(self, value):
        self._check_name(value)
        self.p_name = value

    @property
    def parameter_type(self):
        return self.p_type

    @parameter_type.setter
    def parameter_type(self, value):
        self._check_type(value)
        self.p_type = value

    @property
    def parameter_required(self):
        return self.p_required

    @parameter_required.setter
    def parameter_required(self, value):
        self._check_required(value)
        self.p_required = value

    @property
    def parameter_default(self):
        return self.p_default

    @parameter_default.setter
    def parameter_default(self, value):
        self.p_default = value

    @property
    def value(self):
        return self.value_found

    @value.setter
    def value(self, v):
        self.value_found = v

    def __repr__(self):
        return str(
            {
                'name': self.p_name,
                'type': self.p_type,
                'required': self.p_required,
                'default': self.p_default,
                'value': self.value_found
            }
        )


