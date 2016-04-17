from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from mezzanine.conf import register_setting

register_setting(
    name="SHOP_PRIMARY_COUNTRIES",
    description=_("Countries that show up at the top of the country selection fields. "
                  "A list of alpha2 codes."),
    editable=False,
    default=[]
)

register_setting(
    name="SHOP_SUPPORTED_COUNTRIES",
    description=_("Countries which are supported for billing/shipping. "
                  "A list of alpha2 codes and/or tuples in the form (alpha2, country_name)."),
    editable=False,
    default=[]
)

register_setting(
    name="BRAINTREE_MERCHANT_ID",
    editable=False
)

register_setting(
    name="BRAINTREE_PUBLIC_KEY",
    editable=False
)

register_setting(
    name="BRAINTREE_PRIVATE_KEY",
    editable=False
)

register_setting(
    name="BRAINTREE_PAYPAL_ACTIVATE",
    label=_("Activate PayPal for payment"),
    description=_("If ``True``, PayPal will be included as a payment method."),
    editable=True,
    default=False
)

register_setting(
    name="BRAINTREE_PAYPAL_CURRENCY",
    label=_("Currency for PayPal payments"),
    description=_("The currency Braintree is using for PayPal payments."),
    editable=True,
    default="USD"
    # TODO: Add support for currency selection.
)

register_setting(
    name="TEMPLATE_ACCESSIBLE_SETTINGS",
    editable=False,
    default=("BRAINTREE_PAYPAL_ACTIVATE",
             "BRAINTREE_PAYPAL_CURRENCY"),
    append=True,
)
