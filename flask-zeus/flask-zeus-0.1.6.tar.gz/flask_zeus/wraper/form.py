from flask import request
from flask_wtf import Form as BaseForm
from flask_wtf.form import _Auto
from wtforms import fields
from wtforms import validators
from wtforms.ext.csrf.fields import CSRFTokenField
from wtforms_json import flatten_json
import werkzeug.datastructures


class Form(BaseForm):

    def __init__(self, formdata=_Auto, *args, **kwargs):
        kwargs['csrf_enabled'] = False

        if formdata is _Auto and self.is_submitted() and request.json:
            formdata = flatten_json(self.__class__, request.json)
            formdata = werkzeug.datastructures.MultiDict(formdata)

        super(Form, self).__init__(formdata, *args, **kwargs)

    @classmethod
    def output_field_data_type(cls, field):
        if isinstance(field, (
                fields.HiddenField,
                fields.StringField,
                fields.TextField,
                fields.TextAreaField,
                fields.PasswordField,
                fields.RadioField,
                fields.SelectField,
                fields.SelectMultipleField,
        )):
            return 'str'

        if isinstance(field, (fields.IntegerField,)):
            return 'int'

        if isinstance(field, (fields.FloatField, fields.DecimalField,)):
            return 'float'

        if isinstance(field, (fields.DateField,)):
            return 'date'

        if isinstance(field, (fields.DateTimeField,)):
            return 'datetime'

        if isinstance(field, (fields.BooleanField,)):
            return 'bool'

        if isinstance(field, (fields.FileField,)):
            return 'file'

        if isinstance(field, (fields.FieldList,)):
            return 'list'

        if isinstance(field, (fields.FormField,)):
            return 'form'

        return 'str'

    @classmethod
    def output_validators(cls, field_validators):
        data = []
        for validator in field_validators:
            v_name = validator.__class__.__name__

            if isinstance(validator, validators.Length):
                content = '{} min:{} max:{}'.format(v_name, validator.min, validator.max)

            elif isinstance(validator, validators.Regexp):
                content = '{} regex:{}'.format(v_name, validator.regex.pattern)

            elif isinstance(validator, validators.EqualTo):
                content = '{} to:{}'.format(v_name, validator.fieldname)

            elif isinstance(validator, validators.NumberRange):
                content = '{} range:{}-{}'.format(v_name, validator.min, validator.max)

            elif isinstance(validator, validators.IPAddress):
                content = '{} type:{}'.format(v_name, 'ipv4' if validator.ipv4 else 'ipv6')

            else:
                content = v_name

            data.append(content)

        return data

    @classmethod
    def output_field(cls, field):
        data = dict()
        data['name'] = field.name
        data['text'] = field.label.text
        data['type'] = cls.output_field_data_type(field)

        if field.validators:
            data['validators'] = cls.output_validators(field.validators)

        if field.description:
            data['description'] = field.description

        if field.default is not None:
            data['default'] = field.default

        if isinstance(field, (fields.SelectField, fields.SelectMultipleField, fields.RadioField)):
            data['choices'] = field.choices

        if isinstance(field, (fields.FormField,)):
            data['form'] = cls.output_form(field.form_class(prefix=field.name))

        if isinstance(field, (fields.FieldList,)):
            if field.min_entries:
                data['min_entries'] = field.min_entries

            if field.max_entries:
                data['max_entries'] = field.max_entries

            name = '%s-{n}' % (field.short_name,)
            field = field.unbound_field.bind(form=None, name=name, _meta=field.meta)
            try:
                prefix = field.name + field.separator
                data['form'] = cls.output_form(field.form_class(prefix=prefix))
            except:
                data['field'] = cls.output_field(field)

        return data

    @classmethod
    def output_form(cls, form, **kwargs):
        data = []

        for field in form:
            if field.name in kwargs.keys():
                continue

            if isinstance(field, (fields.SubmitField,)):
                continue

            if not form.csrf_enabled and isinstance(field, (CSRFTokenField,)):
                continue

            data.append(cls.output_field(field))

        return data

    @classmethod
    def fields(cls, **kwargs):
        form = cls()
        return cls.output_form(form, **kwargs)