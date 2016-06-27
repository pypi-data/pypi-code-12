from django.db import models
from django.contrib import admin
from django.core.validators import ValidationError
from django.db.models import fields
from collections import OrderedDict
from django.apps import apps
from django.conf import settings

class App(models.Model):
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=255)
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

def create_model(name, fields=None, app_label='', module='', options=None, admin_opts=None):
    class Meta:
        pass

    if app_label:
        setattr(Meta, 'app_label', app_label)

    if options is not None:
        for key, value in options.iteritems():
            setattr(Meta, key, value)

    attrs = {'__module__': module, 'Meta': Meta}

    if fields:
        attrs.update(fields)

    model = type(name, (models.Model,), attrs)

    if admin_opts is not None:
        class Admin(admin.ModelAdmin):
            pass
        for key, value in admin_opts:
            setattr(Admin, key, value)
        admin.site.register(model, Admin)

    return model

class Model(models.Model):
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)

    def __str__(self):
        return self.name

    def get_django_model(self):
        fields = {}

        map = {
            'DateField': ['auto_now_add', 'auto_now'],
            'DecimalField': ['max_digits', 'decimal_places'],
            'FileField': ['upload_to'],
            'FilePathField': ['path'],
            'ImageField': ['height_field', 'width_field'],
        }

        for f in self.fields.all():

            args = {
                'null': f.field_null,
                'blank': f.field_blank,
                'default': f.field_default,
                'editable': f.field_editable,
                'help_text': f.field_help_text,
                'primary_key': f.field_primary_key,
                'unique': f.field_unique,
                'max_length': f.field_max_length
            }

            if f.field_choices:
                args['choices'] = f.field_choices,

            if f.field_db_column:
                args['db_column'] = f.field_db_column

            if f.field_db_index:
                args['db_index'] = f.field_db_index

            if f.field_verbose_name:
                args['verbose_name'] = f.field_verbose_name

            for key, arguments in map.iteritems():
                if f.my_field == key:
                    for arg in arguments:
                        args.update({arg: eval(f + '.' + arg)})

            fields.update({f.name: eval('models.' + f.my_field)(f.name, **args)})

        new_app_name = self.app.name

        if new_app_name not in settings.INSTALLED_APPS:
            settings.INSTALLED_APPS += (new_app_name, )

            apps.app_configs = OrderedDict()

            apps.ready = False

            apps.populate(settings.INSTALLED_APPS)

        return create_model(str(self.name), dict(fields), app_label=self.app.name, module=self.app.module, admin_opts={})

    class Meta:
        unique_together = (('app', 'name'),)

def is_valid_field(self, field_data, all_data):
    if hasattr(models, field_data) and issubclass(getattr(models, field_data), models.Field):
        return
    raise ValidationError("This is not a valid field type.")

class Field(models.Model):
    model = models.ForeignKey(Model, related_name='fields')
    name = models.CharField(max_length=255)
    my_field = models.CharField(max_length=255, choices=((value, value) for key, value in enumerate(fields.__all__) if value not in ['BLANK_CHOICE_DASH', 'NOT_PROVIDED']))
    field_null = models.BooleanField()
    field_blank = models.BooleanField()
    field_choices = models.CharField(max_length=255, blank=True)
    field_db_column = models.CharField(max_length=255, blank=True)
    field_db_index = models.BooleanField()
    field_default = models.CharField(max_length=255, blank=True)
    field_editable = models.BooleanField(default=True)
    field_help_text = models.CharField(max_length=255, blank=True)
    field_primary_key = models.BooleanField()
    field_unique = models.BooleanField()
    field_verbose_name = models.CharField(max_length=255, blank=True)
    field_max_length = models.IntegerField(default=255)
    field_auto_now_add = models.BooleanField()
    field_auto_now = models.BooleanField()
    field_max_digits = models.IntegerField(default=9)
    field_decimal_places = models.IntegerField(default=0)
    field_upload_to = models.CharField(max_length=255, blank=True)
    field_path = models.CharField(max_length=1000, blank=True)
    field_height_field = models.IntegerField(default=50)
    field_width_field = models.IntegerField(default=50)
    created = models.DateField(auto_now_add=True)
    modified = models.DateField(auto_now=True)

    def get_django_field(self):
        settings = [(s.name, s.value) for s in self.my_field().settings.all()]

        return getattr(models, self.type)(**dict(settings))

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (('model', 'name'),)



