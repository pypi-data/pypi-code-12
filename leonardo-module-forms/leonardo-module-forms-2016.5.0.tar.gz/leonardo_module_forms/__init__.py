
from django.apps import AppConfig


default_app_config = 'leonardo_module_forms.FormConfig'


class Default(object):

    optgroup = ('Forms')

    @property
    def apps(self):
        INSTALLED_APPS = []

        try:
            import captcha  # noqa
        except ImportError:
            pass
        else:
            INSTALLED_APPS += ['captcha']

        try:
            import django_remote_forms  # noqa
        except ImportError:
            pass
        else:
            INSTALLED_APPS += ['django_remote_forms']

        return INSTALLED_APPS + [
            'crispy_forms',
            'form_designer',
            'leonardo_module_forms',
        ]

    @property
    def widgets(self):
        return [
            'leonardo_module_forms.models.FormWidget'
        ]

    @property
    def config(self):
        config = {
            'FORM_FILES_PRIVATE': (True, 'Makes all uploaded files from forms as private'),
            'FORM_FILES_DIRECTORY': ('form files', 'Upload all form files to this directory'),
        }
        try:
            import captcha  # noqa
        except ImportError:
            pass
        else:
            config["RECAPTCHA_PUBLIC_KEY"] = (
                "6LdUAxITAAAAAEXCbUS2OammlZaQv9G5sWmxN0CW", "Recaptcha Public Key")
            config["RECAPTCHA_PRIVATE_KEY"] = (
                "6LdUAxITAAAAAI8oFJ6m5OkYwh_2FhsoBy040-uH", "Recaptcha Private Key")

        return config


class FormConfig(AppConfig):
    name = 'leonardo_module_forms'
    verbose_name = "Module Forms"

    conf = Default()

    def ready(self):

        from form_designer import settings, models
        settings.FORM_DESIGNER_FIELD_TYPES = 'leonardo_module_forms.fields.FIELD_TYPES'
        from .fields import FIELD_TYPES
        models.FIELD_TYPES = FIELD_TYPES

default = Default()
