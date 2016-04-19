from __future__ import absolute_import

import warnings
import re

from django import forms
from django.core import exceptions
from django.forms import FileField

from rest_framework.exceptions import ValidationError

from . import app_settings
from .adapter import get_adapter
from .utils import phone_number_exists, setup_user_phone, get_user_model
from .status import ApiStatus, PHONE_ALREADY_REGISTERED, PHONE_FIELD_REQUIRED, PHONE_NUMBER_INVALID, \
    PHONE_NUMBER_DOES_NOT_EXIST, KEY_FIELD_REQUIRED, PASSWORD_FIELD_REQUIRED, PASSWORD_CONFIRMATION_FIELD_REQUIRED, \
    PASSWORD_MISMATCH, CHANGE_PHONE_NUMBER_EXIST
from .models import QuickPhoneNumber, QuickPhoneConfirmation

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


class _DummyCustomSignupForm(forms.Form):
    def signup(self, request, user):
        """
        Invoked at signup time to complete the signup of the user.
        """
        pass


def _base_signup_form_class():
    """
    Currently, we inherit from the custom form, if any. This is all
    not very elegant, though it serves a purpose:

    - There are two signup forms: one for local accounts, and one for
      social accounts
    - Both share a common base (BaseSignupForm)

    - Given the above, how to put in a custom signup form? Which form
      would your custom form derive from, the local or the social one?
    """
    if not app_settings.SIGNUP_FORM_CLASS:
        return _DummyCustomSignupForm
    try:
        fc_module, fc_classname = app_settings.SIGNUP_FORM_CLASS.rsplit('.', 1)
    except ValueError:
        raise exceptions.ImproperlyConfigured('%s does not point to a form'
                                              ' class'
                                              % app_settings.SIGNUP_FORM_CLASS)
    try:
        mod = import_module(fc_module)
    except ImportError as e:
        raise exceptions.ImproperlyConfigured('Error importing form class %s:'
                                              ' "%s"' % (fc_module, e))
    try:
        fc_class = getattr(mod, fc_classname)
    except AttributeError:
        raise exceptions.ImproperlyConfigured('Module "%s" does not define a'
                                              ' "%s" class' % (fc_module,
                                                               fc_classname))
    if not hasattr(fc_class, 'signup'):
        if hasattr(fc_class, 'save'):
            warnings.warn("The custom signup form must offer"
                          " a `def signup(self, request, user)` method",
                          DeprecationWarning)
        else:
            raise exceptions.ImproperlyConfigured(
                'The custom signup form must implement a "signup" method')
    return fc_class


class PhoneField(forms.CharField):
    def validate(self, value):
        if value in self.empty_values and self.required:
            raise Exception(ApiStatus(PHONE_FIELD_REQUIRED).get_json())

        if len(value) != 11:
            raise Exception(ApiStatus(PHONE_NUMBER_INVALID).get_json())

        china_mobile_pattern = re.compile('^134[0-8]\d{7}$|^(?:13[5-9]|147|15[0-27-9]|178|18[2-478])\d{8}$')
        china_union_pattern = re.compile('^(?:13[0-2]|145|15[56]|176|18[56])\d{8}$')
        china_telcom_pattern = re.compile('^(?:133|153|177|18[019])\d{8}$')
        china_other_pattern = re.compile('^170([059])\d{7}$')

        if not china_mobile_pattern.findall(value) and not china_union_pattern.findall(
                value) and not china_telcom_pattern.findall(value) and not china_other_pattern.findall(value):
            raise Exception(ApiStatus(PHONE_NUMBER_INVALID).get_json())


class BaseSignupForm(_base_signup_form_class()):
    phone = PhoneField(label='Phone', required=True, max_length=256)
    password1 = forms.CharField(label='Password', required=False, max_length=256)
    password2 = forms.CharField(label='Password confirmation', required=False, max_length=256)

    def __init__(self, *args, **kwargs):
        super(BaseSignupForm, self).__init__(*args, **kwargs)

    def clean_phone(self):
        value = self.cleaned_data['phone']
        value = get_adapter().clean_phone(value)
        if app_settings.UNIQUE_PHONE:
            if value and phone_number_exists(value):
                self.raise_duplicate_phone_error()
        return value

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise Exception(ApiStatus(PASSWORD_MISMATCH).get_json())

        return password2

    def raise_duplicate_phone_error(self):
        raise Exception(ApiStatus(PHONE_ALREADY_REGISTERED).get_json())

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if field.disabled:
                value = self.initial.get(name, field.initial)
            else:
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)
            except Exception as e:
                self._errors = e.message

    def custom_signup(self, request, user):
        custom_form = super(BaseSignupForm, self)
        if hasattr(custom_form, 'signup') and callable(custom_form.signup):
            custom_form.signup(request, user)
        else:
            warnings.warn("The custom signup form must offer"
                          " a `def signup(self, request, user)` method",
                          DeprecationWarning)
            # Historically, it was called .save, but this is confusing
            # in case of ModelForm
            custom_form.save(user)


class SignupForm(BaseSignupForm):
    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

    def clean(self):
        super(SignupForm, self).clean()
        return self.cleaned_data

    def save(self, request):
        password1 = self.cleaned_data.get('password1', None)
        password2 = self.cleaned_data.get('password2', None)

        if password1 and password2:
            if password1 != password2:
                self.cleaned_data.pop('password1')
                self.cleaned_data.pop('password2')
        else:
            self.cleaned_data.pop('password1')
            self.cleaned_data.pop('password2')

        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_phone(request, user, [])
        return user


class PasswordResetBaseForm(forms.Form):
    phone = PhoneField(label='Phone', required=True, max_length=256)

    def __init__(self, *args, **kwargs):
        super(PasswordResetBaseForm, self).__init__(*args, **kwargs)

    def clean_phone(self):
        value = self.cleaned_data['phone']
        if not QuickPhoneNumber.objects.filter(phone=value, verified=True).exists():
            raise Exception(ApiStatus(PHONE_NUMBER_DOES_NOT_EXIST).get_json())
        return value

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if field.disabled:
                value = self.initial.get(name, field.initial)
            else:
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)
            except Exception as e:
                self._errors = e.message


class PasswordResetForm(PasswordResetBaseForm):

    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def save(self):
        phone = self.cleaned_data['phone']
        active_users = get_user_model()._default_manager.filter(
            **{app_settings.USER_MODEL_PHONE_FIELD + '__iexact': phone, 'is_active': True})

        if active_users.exists():
            return active_users[0]
        else:
            return None


class SetPasswordForm(PasswordResetBaseForm):
    key = forms.CharField(label='Key', required=False, max_length=256)
    new_password1 = forms.CharField(label='New password', required=False, max_length=256)
    new_password2 = forms.CharField(label='New password confirmation', required=False, max_length=256)

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_key(self):
        key = self.cleaned_data.get('key')

        if not key:
            raise Exception(ApiStatus(KEY_FIELD_REQUIRED).get_json())

        return key

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')

        if not password1:
            raise Exception(ApiStatus(PASSWORD_FIELD_REQUIRED).get_json())

        return password1

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')

        if not password1:
            raise Exception(ApiStatus(PASSWORD_FIELD_REQUIRED).get_json())

        if not password2:
            raise Exception(ApiStatus(PASSWORD_CONFIRMATION_FIELD_REQUIRED).get_json())

        if password1 != password2:
            raise Exception(ApiStatus(PASSWORD_MISMATCH).get_json())

        return password2

    def save(self, commit=True):
        phone = self.cleaned_data['phone']
        key = self.cleaned_data['key']
        password = self.cleaned_data['new_password2']

        queryset = QuickPhoneConfirmation.objects.filter(phone_number__phone=phone)
        queryset = queryset.select_related('phone_number__user')

        try:
            return queryset.get(key=key.lower()), password
        except QuickPhoneConfirmation.DoesNotExist:
            return None, password


class ChangePhoneForm(forms.Form):
    phone = PhoneField(label='Phone', required=True, max_length=256)

    def __init__(self, *args, **kwargs):
        super(ChangePhoneForm, self).__init__(*args, **kwargs)

    def clean_phone(self):
        value = self.cleaned_data['phone']
        return value

    def _clean_fields(self):
        for name, field in self.fields.items():
            # value_from_datadict() gets the data from the data dictionaries.
            # Each widget type knows how to retrieve its own data, because some
            # widgets split data over several HTML fields.
            if field.disabled:
                value = self.initial.get(name, field.initial)
            else:
                value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
            try:
                if isinstance(field, FileField):
                    initial = self.initial.get(name, field.initial)
                    value = field.clean(value, initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, 'clean_%s' % name):
                    value = getattr(self, 'clean_%s' % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)
            except Exception as e:
                self._errors = e.message