from django.conf import settings
from django.core import serializers
from django.db.models.fields import FieldDoesNotExist
from mint import utils


class Serializer(object):
    def __init__(self, model, include=[]):
        self.model = model
        self.include = include

    def pack(self):
        if len(self.include) > 0:
            fields = serializers.serialize('python', (self.model, ), fields=self.include)[0]['fields']
        else:
            fields = serializers.serialize('python', (self.model, ))[0]['fields']
        for name, value in fields.items():
            try:
                my_type = self.model._meta.get_field(name).get_internal_type()
                if my_type == 'DateTimeField':
                    fields[name] = utils.string_from_datetime(value)
                elif my_type == 'DateField':
                    fields[name] = utils.string_from_datetime(value)
                elif my_type == 'TimeField':
                    fields[name] = utils.string_from_time(value)
                elif my_type == 'DecimalField':
                    fields[name] = float(value)
                elif my_type == 'FileField':
                    fields[name] = "%s%s" % (settings.MEDIA_URL, value)
                elif my_type in ('ForeignKey',):
                    key = "%s_id" % name
                    fields[key] = value
                    del fields[name]
                elif hasattr(self.model, 'get_%s_display' % name):
                    fields[name] = getattr(self.model, 'get_%s_display' % name)()
            except FieldDoesNotExist:
                pass
        fields['id'] = self.model.id
        fields['model'] = utils.camel_to_underscore(self.model.__class__.__name__)
        return fields