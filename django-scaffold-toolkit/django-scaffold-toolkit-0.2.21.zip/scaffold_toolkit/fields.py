# coding=utf-8
from django.contrib.admin.widgets import AdminTextInputWidget
from django.db.models import CharField
import shortuuid

from scaffold_toolkit.forms.tagfield import TagAutocompleteInput
from tagging.fields import TagField


class TagAutocompleteField(TagField):
    def formfield(self, **kwargs):
        defaults = {'widget': TagAutocompleteInput}
        defaults.update(kwargs)
        # As an ugly hack, we override the admin widget
        if defaults['widget'] == AdminTextInputWidget:
            defaults['widget'] = TagAutocompleteInput(attrs={'class': 'vTextField'})
        return super(TagAutocompleteField, self).formfield(**defaults)


class ShortUUIDField(CharField):
    """
    A field which stores a Short UUID value in base57 format. This may also have
    the Boolean attribute 'auto' which will set the value on initial save to a
    new UUID value (calculated using shortuuid's default (uuid4)). Note that while all
    UUIDs are expected to be unique we enforce this with a DB constraint.
    """

    def __init__(self, auto=True, *args, **kwargs):
        self.auto = auto
        # We store UUIDs in base57 format, which is fixed at 22 characters.
        kwargs['max_length'] = 22
        if auto:
            # Do not let the user edit UUIDs if they are auto-assigned.
            kwargs['editable'] = False
            kwargs['blank'] = True
            # kwargs['unique'] = True  # if you want to be paranoid, set unique=True in your instantiation of the field.

        super(ShortUUIDField, self).__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        """
        This is used to ensure that we auto-set values if required.
        See CharField.pre_save
        """
        value = super(ShortUUIDField, self).pre_save(model_instance, add)
        if self.auto and not value:
            # Assign a new value for this attribute if required.
            value = shortuuid.uuid()
            setattr(model_instance, self.attname, value)
        return value

    def formfield(self, **kwargs):
        if self.auto:
            return None
        return super(ShortUUIDField, self).formfield(**kwargs)
