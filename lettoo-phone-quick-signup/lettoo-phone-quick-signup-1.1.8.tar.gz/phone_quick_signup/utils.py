import re
import unicodedata
from datetime import timedelta

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime

    now = datetime.now

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import ValidationError
from django.utils import six
from django.utils.translation import ugettext_lazy as _

try:
    from django.utils.encoding import force_text, force_bytes
except ImportError:
    from django.utils.encoding import force_unicode as force_text

try:
    import importlib
except ImportError:
    from django.utils import importlib


def _generate_unique_username_base(txts, regex=None):
    from .adapter import get_adapter
    adapter = get_adapter()
    username = None
    regex = regex or '[^\w\s@+.-]'
    for txt in txts:
        if not txt:
            continue
        username = unicodedata.normalize('NFKD', force_text(txt))
        username = username.encode('ascii', 'ignore').decode('ascii')
        username = force_text(re.sub(regex, '', username).lower())
        username = username.split('@')[0]
        username = username.strip()
        username = re.sub('\s+', '_', username)
        # Finally, validating base username without database lookups etc.
        try:
            username = adapter.clean_username(username, shallow=True)
            break
        except ValidationError:
            pass
    return username or 'user'


def get_username_max_length():
    from . import app_settings
    if app_settings.USER_MODEL_USERNAME_FIELD is not None:
        User = get_user_model()
        max_length = User._meta.get_field(app_settings.USER_MODEL_USERNAME_FIELD).max_length
    else:
        max_length = 0
    return max_length


def generate_unique_username(txts, regex=None):
    from .adapter import get_adapter
    adapter = get_adapter()
    username = _generate_unique_username_base(txts, regex)
    max_length = get_username_max_length()
    i = 0
    while True:
        try:
            if i:
                pfx = str(i + 1)
            else:
                pfx = ''
            ret = username[0:max_length - len(pfx)] + pfx
            return adapter.clean_username(ret)
        except ValidationError:
            i += 1


def valid_phone_or_none(phone):
    ret = None
    try:
        if phone:
            ret = phone
    except ValidationError:
        pass
    return ret


def phone_number_exists(phone, exclude_user=None):
    from . import app_settings
    from .models import QuickPhoneNumber

    phone_numbers = QuickPhoneNumber.objects
    if exclude_user:
        phone_numbers = phone_numbers.exclude(user=exclude_user)
    ret = phone_numbers.filter(phone__iexact=phone).exists()
    if not ret:
        phone_field = app_settings.USER_MODEL_PHONE_FIELD
        if phone_field:
            users = get_user_model().objects
            if exclude_user:
                users = users.exclude(pk=exclude_user.pk)
            ret = users.filter(**{phone_field + '__iexact': phone}).exists()
    return ret


def import_attribute(path):
    assert isinstance(path, six.string_types)
    pkg, attr = path.rsplit('.', 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


try:
    from django.contrib.auth import get_user_model
except ImportError:
    # To keep compatibility with Django 1.4
    def get_user_model():
        from . import app_settings
        from django.db.models import get_model

        try:
            app_label, model_name = app_settings.USER_MODEL.split('.')
        except ValueError:
            raise ImproperlyConfigured("AUTH_USER_MODEL must be of the"
                                       " form 'app_label.model_name'")
        user_model = get_model(app_label, model_name)
        if user_model is None:
            raise ImproperlyConfigured("AUTH_USER_MODEL refers to model"
                                       " '%s' that has not been installed"
                                       % app_settings.USER_MODEL)
        return user_model


def get_form_class(forms, form_id, default_form):
    form_class = forms.get(form_id, default_form)
    if isinstance(form_class, six.string_types):
        form_class = import_attribute(form_class)
    return form_class


def user_field(user, field, *args):
    """
    Gets or sets (optional) user model fields. No-op if fields do not exist.
    """
    if field and hasattr(user, field):
        if args:
            # Setter
            v = args[0]
            if v:
                User = get_user_model()
                if isinstance(v, str):
                    v = v[0:User._meta.get_field(field).max_length]
            setattr(user, field, v)
        else:
            # Getter
            return getattr(user, field)


def user_username(user, *args):
    from . import app_settings
    return user_field(user, app_settings.USER_MODEL_USERNAME_FIELD, *args)


def user_phone(user, *args):
    from . import app_settings
    return user_field(user, app_settings.USER_MODEL_PHONE_FIELD, *args)


def user_phone_verified(user, *args):
    from . import app_settings
    return user_field(user, app_settings.USER_MODEL_PHONE_VERIFIED_FIELD, *args)


def cleanup_phone_numbers(request, numbers):
    from collections import OrderedDict
    from .models import QuickPhoneNumber
    from . import app_settings

    e2a = OrderedDict()
    primary_numbers = []
    verified_numbers = []
    primary_verified_numbers = []
    for number in numbers:
        # Pick up only valid ones...
        phone = valid_phone_or_none(number.phone)
        if not phone:
            continue
        # ... and non-conflicting ones...
        if app_settings.UNIQUE_PHONE and QuickPhoneNumber.objects.filter(phone__iexact=phone).exists():
            continue
        a = e2a.get(phone.lower())
        if a:
            a.primary = a.primary or number.primary
            a.verified = a.verified or number.verified
        else:
            a = number
            e2a[phone.lower()] = a
        if a.primary:
            primary_numbers.append(a)
            if a.verified:
                primary_verified_numbers.append(a)
        if a.verified:
            verified_numbers.append(a)
    # Now that we got things sorted out, let's assign a primary
    if primary_verified_numbers:
        primary_number = primary_verified_numbers[0]
    elif verified_numbers:
        # Pick any verified as primary
        primary_number = verified_numbers[0]
    elif primary_numbers:
        # Okay, let's pick primary then, even if unverified
        primary_number = primary_numbers[0]
    elif e2a:
        # Pick the first
        primary_number = e2a.keys()[0]
    else:
        # Empty
        primary_number = None
    # There can only be one primary
    for a in e2a.values():
        a.primary = primary_number.phone.lower() == a.phone.lower()
    return list(e2a.values()), primary_number


def send_phone_confirmation(user=None, phone_number=None, check_verified=True):
    from .models import QuickPhoneNumber, QuickPhoneConfirmation
    from . import app_settings

    send_sms = False
    cooldown_period = timedelta(minutes=app_settings.RESEND_CONFIRMATION_COOLDOWN_PERIOD_MINUTES)

    if not phone_number:
        phone = user_phone(user)

        try:
            phone_number = QuickPhoneNumber.objects.get_for_user(user, phone)
        except QuickPhoneNumber.DoesNotExist:
            send_sms = True
            QuickPhoneNumber.objects.add_phone(user, phone, confirm=True)

    if not send_sms:
        if not phone_number.verified or not check_verified:
            send_sms = not QuickPhoneConfirmation.objects.filter(sent__gt=now() - cooldown_period,
                                                                 phone_number=phone_number).exists()
            if send_sms:
                phone_number.send_confirmation()
            else:
                send_sms = False

    return send_sms


def setup_user_phone(request, user, numbers):
    from .models import QuickPhoneNumber

    assert QuickPhoneNumber.objects.filter(user=user).count() == 0
    priority_numbers = []
    phone = user_phone(user)
    if phone:
        priority_numbers.append(QuickPhoneNumber(user=user,
                                                 phone=phone,
                                                 primary=True,
                                                 verified=False))
    numbers, primary = cleanup_phone_numbers(request,
                                             priority_numbers + numbers)
    for a in numbers:
        a.user = user
        a.save()
    QuickPhoneNumber.objects.fill_cache_for_user(user, numbers)
    if primary and phone and phone.lower() != primary.phone.lower():
        user_phone(user, primary.phone)
        user.save()
    return primary