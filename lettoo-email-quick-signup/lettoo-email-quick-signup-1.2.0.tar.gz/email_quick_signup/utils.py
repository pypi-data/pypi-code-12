import base64
import re
import unicodedata
import json
from datetime import timedelta

try:
    from django.utils.timezone import now
except ImportError:
    from datetime import datetime

    now = datetime.now

from django.core.exceptions import ImproperlyConfigured
from django.core.validators import validate_email, ValidationError
from django.core import urlresolvers
from django.contrib.sites.models import Site
from django.db.models import FieldDoesNotExist
from django.db.models.fields import (DateTimeField, DateField,
                                     EmailField, TimeField,
                                     BinaryField)
from django.utils import six, dateparse
from django.utils.translation import ugettext_lazy as _

from django.core.serializers.json import DjangoJSONEncoder

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
        # Django allows for '@' in usernames in order to accomodate for
        # project wanting to use e-mail for username. In allauth we don't
        # use this, we already have a proper place for putting e-mail
        # addresses (EmailAddress), so let's not use the full e-mail
        # address and only take the part leading up to the '@'.
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


def valid_email_or_none(email):
    ret = None
    try:
        if email:
            validate_email(email)
            if len(email) <= EmailField().max_length:
                ret = email
    except ValidationError:
        pass
    return ret


def email_address_exists(email, exclude_user=None):
    from . import app_settings
    from .models import QuickEmailAddress

    emailaddresses = QuickEmailAddress.objects
    if exclude_user:
        emailaddresses = emailaddresses.exclude(user=exclude_user)
    ret = emailaddresses.filter(email__iexact=email).exists()
    if not ret:
        email_field = app_settings.USER_MODEL_EMAIL_FIELD
        if email_field:
            users = get_user_model().objects
            if exclude_user:
                users = users.exclude(pk=exclude_user.pk)
            ret = users.filter(**{email_field + '__iexact': email}).exists()
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


def get_current_site(request=None):
    """Wrapper around ``Site.objects.get_current`` to handle ``Site`` lookups
    by request in Django >= 1.8.

    :param request: optional request object
    :type request: :class:`django.http.HttpRequest`
    """
    # >= django 1.8
    if request and hasattr(Site.objects, '_get_site_by_request'):
        site = Site.objects.get_current(request=request)
    else:
        site = Site.objects.get_current()

    return site


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


def user_email(user, *args):
    from . import app_settings
    return user_field(user, app_settings.USER_MODEL_EMAIL_FIELD, *args)


def user_email_verified(user, *args):
    from . import app_settings
    return user_field(user, app_settings.USER_MODEL_EMAIL_VERIFIED_FIELD, *args)


def cleanup_email_addresses(request, addresses):
    """
    Takes a list of EmailAddress instances and cleans it up, making
    sure only valid ones remain, without multiple primaries etc.

    Order is important: e.g. if multiple primary e-mail addresses
    exist, the first one encountered will be kept as primary.
    """
    from collections import OrderedDict
    from .models import QuickEmailAddress
    from .adapter import get_adapter
    from . import app_settings

    adapter = get_adapter()
    # Let's group by `email`
    e2a = OrderedDict()  # maps email to EmailAddress
    primary_addresses = []
    verified_addresses = []
    primary_verified_addresses = []
    for address in addresses:
        # Pick up only valid ones...
        email = valid_email_or_none(address.email)
        if not email:
            continue
        # ... and non-conflicting ones...
        if app_settings.UNIQUE_EMAIL and QuickEmailAddress.objects.filter(email__iexact=email).exists():
            continue
        a = e2a.get(email.lower())
        if a:
            a.primary = a.primary or address.primary
            a.verified = a.verified or address.verified
        else:
            a = address
            e2a[email.lower()] = a
        if a.primary:
            primary_addresses.append(a)
            if a.verified:
                primary_verified_addresses.append(a)
        if a.verified:
            verified_addresses.append(a)
    # Now that we got things sorted out, let's assign a primary
    if primary_verified_addresses:
        primary_address = primary_verified_addresses[0]
    elif verified_addresses:
        # Pick any verified as primary
        primary_address = verified_addresses[0]
    elif primary_addresses:
        # Okay, let's pick primary then, even if unverified
        primary_address = primary_addresses[0]
    elif e2a:
        # Pick the first
        primary_address = e2a.keys()[0]
    else:
        # Empty
        primary_address = None
    # There can only be one primary
    for a in e2a.values():
        a.primary = primary_address.email.lower() == a.email.lower()
    return list(e2a.values()), primary_address


def send_email_confirmation(request, user=None, email_address=None, signup=False, check_verified=True):
    """
    E-mail verification mails are sent:
    a) Explicitly: when a user signs up
    b) Implicitly: when a user attempts to log in using an unverified
    e-mail while EMAIL_VERIFICATION is mandatory.

    Especially in case of b), we want to limit the number of mails
    sent (consider a user retrying a few times), which is why there is
    a cooldown period before sending a new mail.
    """
    from .models import QuickEmailAddress, QuickEmailConfirmation
    from . import app_settings

    send_email = False
    cooldown_period = timedelta(minutes=app_settings.RESEND_CONFIRMATION_COOLDOWN_PERIOD_MINUTES)

    if not email_address:
        email = user_email(user)

        try:
            email_address = QuickEmailAddress.objects.get_for_user(user, email)
        except QuickEmailAddress.DoesNotExist:
            send_email = True
            QuickEmailAddress.objects.add_email(request, user, email, signup=signup, confirm=True)

    if not send_email:
        if not email_address.verified or not check_verified:
            send_email = not QuickEmailConfirmation.objects.filter(sent__gt=now() - cooldown_period,
                                                                   email_address=email_address).exists()
            if send_email:
                email_address.send_confirmation(request, signup=signup)
            else:
                send_email = False

    return send_email


def setup_user_email(request, user, addresses):
    """
    Creates proper EmailAddress for the user that was just signed
    up. Only sets up, doesn't do any other handling such as sending
    out email confirmation mails etc.
    """
    from .models import QuickEmailAddress

    assert QuickEmailAddress.objects.filter(user=user).count() == 0
    priority_addresses = []
    email = user_email(user)
    if email:
        priority_addresses.append(QuickEmailAddress(user=user,
                                                    email=email,
                                                    primary=True,
                                                    verified=False))
    addresses, primary = cleanup_email_addresses(request,
                                                 priority_addresses + addresses)
    for a in addresses:
        a.user = user
        a.save()
    QuickEmailAddress.objects.fill_cache_for_user(user, addresses)
    if primary and email and email.lower() != primary.email.lower():
        user_email(user, primary.email)
        user.save()
    return primary


def complete_signup(request, user):
    from .models import QuickEmailAddress

    has_verified_email = QuickEmailAddress.objects.filter(user=user, verified=True).exists()
    if not has_verified_email:
        send_email_confirmation(request, user, signup=True)
