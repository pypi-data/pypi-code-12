from django.db.models import AutoField, PositiveIntegerField, IntegerField, PositiveSmallIntegerField, CharField, \
    TextField, DateField, DateTimeField, TimeField, DecimalField, BooleanField, EmailField
from django.db.models.fields.related import ForeignKey
from django.forms import FileField, ImageField

class ConfigField(object):
    def __init__(self, klass, name, label, show, description=''):
        self.maxLength = 0
        self.label = label
        self.show = show
        self.validators = []
        self.options = []
        self.description = description
        field = self.get_field_from_class(klass, name)
        self.config(field)


    def get_field_from_class(self, cls, fieldname):
        for f in cls._meta.fields:
            if f.name == fieldname:
                return f

    def config(self, field):

        self.name = field.attname
        self.maxLength = field.max_length
        self.editable = field.editable,

        # Type of field
        if isinstance(field, (AutoField, PositiveIntegerField, IntegerField, PositiveSmallIntegerField)):
            self.type = 'integer'
        elif isinstance(field, CharField):
            self.type = 'string'
        elif isinstance(field, TextField):
            self.type = 'text'
        elif isinstance(field, DateField):
            self.type = 'date'
        elif isinstance(field, DateTimeField):
            self.type = 'datetime'
        elif isinstance(field, TimeField):
            self.type = 'time'
        elif isinstance(field, DecimalField):
            self.type = 'double'
        elif isinstance(field, BooleanField):
            self.type = 'boolean'
        elif isinstance(field, EmailField):
            self.type = 'email'
        elif isinstance(field, FileField):
            self.type = 'file'
        elif isinstance(field, ImageField):
            self.type = 'image'
        elif isinstance(field, ForeignKey):
            self.type = 'fk'

        if field.choices:
            self.type = 'combobox'
            for op in field.choices:
                self.options.append({'caption': op[1],
                                     'value': op[0]})
                if len(op[1]) > field.max_length:
                    self.maxLength = len(op[1])

        if field.null == False:
            validation = {
                'type': 'notnull',
                'message': 'Esse campo nao pode fica vazio'  # f.error_messages['null']
            }
            self.validators.append(validation)

        for v in field.validators:
            validation = None
            if v.code == 'min_length':
                validation = {
                    'type': 'min_length',
                    'value': v.limit_value,
                    'message': 'Digite no minimo {0} caracteres'.format(v.limit_value)
                }


            elif v.code == 'max_length':
                validation = {
                    'type': 'max_length',
                    'value': v.limit_value,
                    'message': 'Digite no maximo {0} caracteres'.format(v.limit_value)
                }


            elif v.code == 'max_value':
                validation = {
                    'type': 'max_value',
                    'value': v.limit_value,
                    'message': str(v.message)
                }

            elif v.code == 'min_value':
                validation = {
                    'type': 'min_value',
                    'value': v.limit_value,
                    'message': str(v.message)
                }

            if validation:
                self.validators.append(validation)
