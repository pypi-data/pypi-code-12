from django.db import models
import GenSettingDict


class SettingsField(models.TextField):

    description = "field that holds serialized settings"

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(SettingsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        database value to python datatype
        """
        if isinstance(value, GenSettingDict.GenSettingDict):
            return value

        try:
            return GenSettingDict.GenSettingDict.deserialize(value)
        except:
            return GenSettingDict.GenSettingDict()

    def get_prep_value(self, value):
        """
        python datatype to database value
        """
        if isinstance(value, GenSettingDict.GenSettingDict):
            return value.serialize()
        else:
            raise TypeError("value must be of type GenSettingDict")

    def get_prep_lookup(self, lookup_type, value):
        """
        no support for lookup yet, maybe in or contains for settings
        """
        raise TypeError('Lookup type %r not supported.' % lookup_type)

