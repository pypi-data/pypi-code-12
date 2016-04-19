from __future__ import unicode_literals

import re

from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django import forms

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text

from .utils import import_attribute, get_user_model, generate_unique_username
from . import app_settings

# Don't bother turning this into a setting, as changing this also
# requires changing the accompanying form error message. So if you
# need to change any of this, simply override clean_username().
USERNAME_REGEX = re.compile(r'^[\w.@+-]+$', re.UNICODE)


class DefaultAccountAdapter(object):
    def new_user(self, request):
        """
        Instantiates a new User instance.
        """
        user = get_user_model()()
        return user

    def populate_username(self, request, user):
        """
        Fills in a valid username, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        from .utils import user_username, user_phone
        phone = user_phone(user)
        username = user_username(user)
        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username(user, username or self.generate_unique_username([phone, 'user']))

    def generate_unique_username(self, txts, regex=None):
        return generate_unique_username(txts, regex)

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from .utils import user_phone

        data = form.cleaned_data
        phone = data.get('phone')
        user_phone(user, phone)
        if 'password1' in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        if commit:
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user

    def clean_username(self, username, shallow=False):
        """
        Validates the username. You can hook into this if you want to
        (dynamically) restrict what usernames can be chosen.
        """
        if not USERNAME_REGEX.match(username):
            raise forms.ValidationError(_("Usernames can only contain "
                                          "letters, digits and @/./+/-/_."))

        # TODO: Add regexp support to USERNAME_BLACKLIST
        username_blacklist_lower = [ub.lower()
                                    for ub in app_settings.USERNAME_BLACKLIST]
        if username.lower() in username_blacklist_lower:
            raise forms.ValidationError(_("Username can not be used. "
                                          "Please use other username."))
        # Skipping database lookups when shallow is True, needed for unique
        # username generation.
        if not shallow:
            username_field = app_settings.USER_MODEL_USERNAME_FIELD
            assert username_field
            user_model = get_user_model()
            try:
                query = {username_field + '__iexact': username}
                user_model.objects.get(**query)
            except user_model.DoesNotExist:
                return username
            raise forms.ValidationError(
                _("This username is already taken. Please choose another."))
        return username

    def clean_phone(self, phone):
        """
        Validates an phone value. You can hook into this if you want to
        (dynamically) restrict what phone number can be chosen.
        """
        return phone

    def clean_password(self, password):
        """
        Validates a password. You can hook into this if you want to
        restric the allowed password choices.
        """
        min_length = app_settings.PASSWORD_MIN_LENGTH
        if len(password) < min_length:
            raise forms.ValidationError(_("Password must be a minimum of {0} "
                                          "characters.").format(min_length))
        return password

    def confirm_phone(self, request, phone_number):
        """
        Marks the phone number as confirmed on the db
        """
        from .utils import user_phone_verified

        phone_number.verified = True
        phone_number.set_as_primary(conditional=False)
        phone_number.save()

        # Set phone verified field is True
        user_phone_verified(phone_number.user, True)
        phone_number.user.save()

    def set_password(self, user, password):
        user.set_password(password)
        user.save()

    def get_user_search_fields(self):
        user = get_user_model()()
        return filter(lambda a: a and hasattr(user, a),
                      [app_settings.USER_MODEL_USERNAME_FIELD,
                       'first_name', 'last_name', 'phone'])

    def get_connection(self, fail_silently=False, **kwargs):
        """
        Load an sms backend and return an instance of it.

        :param string path: backend python path. Default: sendsms.backends.console.SmsBackend
        :param bool fail_silently: Flag to not throw exceptions on error. Default: False
        :returns: backend class instance.
        :rtype: :py:class:`~sendsms.backends.base.BaseSmsBackend` subclass
        """

        try:
            klass = import_attribute(app_settings.SENDSMS_BACKEND)
        except AttributeError:
            raise ImproperlyConfigured(_(u'Error importing sms backend module'))

        return klass(fail_silently=fail_silently, **kwargs)

    def send_sms(self, body, params, from_phone, to, connection):
        """
        Sends the sms message
        """
        if not to:
            return 0
        res = connection.send_messages([{
            'body': body,
            'params': params,
            'from_phone': from_phone,
            'to': to
        }])
        return res

    def send_confirmation_sms(self, key, body=None, from_phone=None, to=[], fail_silently=False, auth_user=None,
                              auth_password=None, connection=None):
        """
        Easy wrapper for send a single SMS to a recipient list.

        :returns: the number of SMSs sent.
        """

        to = list(to)
        from_phone = from_phone or app_settings.SENDSMS_DEFAULT_FROM_PHONE
        body = body or app_settings.SENDSMS_DEFAULT_BODY
        params = {
            'key': str(key),
            'expire_minutes': str(app_settings.PHONE_CONFIRMATION_EXPIRE_MINUTES)
        }

        connection = connection or self.get_connection(
            username=auth_user,
            password=auth_password,
            fail_silently=fail_silently
        )
        return self.send_sms(body=body, params=params, from_phone=from_phone, to=to, connection=connection)


def get_adapter():
    return import_attribute(app_settings.ADAPTER)()
