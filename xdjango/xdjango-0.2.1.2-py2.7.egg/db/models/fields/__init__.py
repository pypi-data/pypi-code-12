from django.db.models import CharField
from django.utils.translation import ugettext_lazy as _

from xdjango.core.validators import validate_phone_number


class PhoneNumberField(CharField):
    default_validators = [validate_phone_number]
    description = _("Phone number")

    def __init__(self, *args, **kwargs):
        # max_length=254 to be compliant with RFCs 3696 and 5321
        kwargs['max_length'] = kwargs.get('max_length', 15)
        super(PhoneNumberField, self).__init__(*args, **kwargs)