from flask_restful import fields


class FieldMixin(fields.Raw):

    def __init__(self, prompt='', *args, **kwargs):
        self.prompt = prompt
        super().__init__(*args, **kwargs)


class Raw(FieldMixin, fields.Raw):
    pass


class Integer(FieldMixin, fields.Integer):
    pass


class String(FieldMixin, fields.String):
    pass


class Url(FieldMixin, fields.Url):

    def __init__(self, prompt='', *args, **kwargs):
        kwargs['absolute'] = True
        super().__init__(prompt, *args, **kwargs)


class Boolean(FieldMixin, fields.Boolean):
    pass


class FormattedString(FieldMixin, fields.FormattedString):
    pass


class Float(FieldMixin, fields.Float):
    pass


class Arbitrary(FieldMixin, fields.Arbitrary):
    pass


class DateTime(FieldMixin, fields.DateTime):

    def __init__(self, prompt='', *args, **kwargs):
        kwargs['dt_format'] = 'iso8601'
        super().__init__(prompt, *args, **kwargs)


class Fixed(FieldMixin, fields.Fixed):
    pass


class List(fields.List):
    pass


class Nested(fields.Nested):
    pass

