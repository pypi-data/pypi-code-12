import os.path

ATTR_KEYS = [
    'activity',
    'product',
    'institute',
    'model',
    'experiment',
    'frequency',
    'modeling_realm',
    'mip_table',
    'ensemble_member',
    'version_number',
    'variable_name',
    'temporal_subset',
    'geographical_info',
    't_start',
    't_end',
    'temporal_suffix'
]


class CmipFile(object):
    """Represents a CmipFile.

    Provides common functionality for children.

    Arguments:
        nc_fp (Optional[str]): A netCDF file path to pull attributes from internal metadata.
        **kwargs: Keyworded metadata (overrides any meta obtained from path args)
    """

    def __init__(self, nc = None, **kwargs):
        """Initializes a CmipFile

        """
        meta = {}
        if nc:
            meta.update(get_nc_attrs(nc))

        meta.update(kwargs)
        self.update(**meta)

    def __repr__(self):
        s = self.__class__.__name__ + "("
        args = ", ".join(["{} = '{}'".format(k, v) for k, v in self.__dict__.items() if k in ATTR_KEYS])
        s += args + ")"
        return s

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
            and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def _update_known_atts(self, **kwargs):
        """Updates instance attributes with supplied keyword arguments.
        """
        for k, v in kwargs.items():
            if k not in ATTR_KEYS:
                # Warn if passed in unknown kwargs
                raise SyntaxWarning('Unknown argument: {}'.format(k))
            elif not v: # Delete attributes with falsey values
                delattr(self, k)
            else:
                setattr(self, k, v)

    def update(self, **kwargs):
        """Updates instance attributes with supplied keyword arguments.

        If a supplied value is falsey, the attribute will be deleted.

        Arguments:
            **kwargs (dict): keyword arguments to update instance with

        Raises:
            SyntaxWarning: If a supplied key is not recognized as valid metadata
        """

        self._update_known_atts(**kwargs)

    def delete(self, *args):
        """Delete instance metadata by attribute name.
        """

        self._update_known_atts(**{k: False for k in args})

    @property
    def atts(self):
        return {k: v for k, v in self.__dict__.items() if k in ATTR_KEYS}

    # Temporal subset elements
    def set_timeval(self, index, value):
        if self.temporal_subset:
            l = self.temporal_subset.split('-')
            l[index] = value
            self.temporal_subset = '-'.join(l)

    @property
    def t_start(self):
        if self.temporal_subset:
            return self.temporal_subset.split('-')[0]

    @t_start.setter
    def t_start(self, value):
        self.set_timeval(0, value)

    @property
    def t_end(self):
        if self.temporal_subset:
            return self.temporal_subset.split('-')[1]

    @t_end.setter
    def t_end(self, value):
        self.set_timeval(1, value)

    @property
    def temporal_suffix(self):
        if self.temporal_subset and len(self.temporal_subset.split('-')) > 2:
            return self.temporal_subset.split('-')[2]
        else:
            return None

    @temporal_suffix.setter
    def temporal_suffix(self, value):
        if self.temporal_subset:
            l = self.temporal_subset.split('-')
            if self.temporal_suffix: # Replace temporal_suffix if exists, else append to temporal_subset
                l[2] = value
            else:
                l.append(value)

            self.temporal_subset = '-'.join(l)

    def get_joined_dir_name(self, atts):
        """Returns a joined path populated with the supplied attribute names
        """

        return os.path.join(*[getattr(self, x) for x in atts])

    def get_joined_file_name(self, atts, optional_atts = None):
        """Returns a joined path populated with the supplied attribute names
        """

        return '_'.join(
            [getattr(self, x) for x in atts] +
            [getattr(self, x) for x in optional_atts if x in self.__dict__]
        ) + '.nc'

def get_nc_attrs(nc):
    """Gets netCDF file metadata attributes.

    Arguments:
        nc (netCDF4.Dataset): an open NetCDF4 Dataset to pull attributes from.

    Returns:
        dict: Metadata as extracted from the netCDF file.
    """

    meta = {
        'experiment': nc.experiment_id,
        'frequency': nc.frequency,
        'institute': nc.institute_id,
        'model': nc.model_id,
        'modeling_realm': nc.modeling_realm,
        'ensemble_member': 'r{}i{}p{}'.format(nc.realization, nc.initialization_method, nc.physics_version),
    }

    variable_name = get_var_name(nc)
    if variable_name:
        meta.update({'variable_name': variable_name})

    return meta

def get_var_name(nc):
    """Guesses the variable_name of an open NetCDF file
    """

    non_variable_names = [
        'lat',
        'lat_bnds',
        'lon',
        'lon_bnds',
        'time',
        'latitude',
        'longitude',
        'bnds'
    ]

    _vars = set(nc.variables.keys())
    _vars.difference_update(set(non_variable_names))
    if len(_vars) == 1:
        return _vars.pop()
    return None