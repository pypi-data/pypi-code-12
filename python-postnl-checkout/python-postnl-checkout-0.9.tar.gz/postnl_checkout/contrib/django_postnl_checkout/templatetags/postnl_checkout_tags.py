from django import template
from django.utils.translation import get_language

from ..settings import postnl_checkout_settings
from ..models import Order

register = template.Library()


@register.simple_tag(takes_context=True)
def get_postnl_checkout(context):
    """
    Add 'postnl_checkout' variable to context, with properties:

    * `active`: boolean whether or not the service is active (ping_status).
    * `js_url`: URL of JS file in current environment.
    * `js_environment`: Name of current environment.
    * `button_url`: URL to active/inactive button image.
    """

    button_base = 'https://checkout.postnl.nl/checkoutbutton/'
    checkout_js = 'Checkout2/Scripts/Checkout.js'

    service_status = Order.ping_status()
    active = service_status and (get_language() == 'nl')

    data = {
        'active': active
    }

    if active:
        data['button_url'] = button_base + 'bt_postnl_checkout.png'
    else:
        data['button_url'] = button_base + 'bt_postnl_checkout_inactief.png'

    if postnl_checkout_settings.ENVIRONMENT == 'production':
        data.update({
            'js_url': 'https://mijnpakket.postnl.nl/' + checkout_js,
            'js_environment': 'PostNL_OP_Checkout.environment_production'
        })

    else:
        assert postnl_checkout_settings.ENVIRONMENT == 'sandbox', \
            'Unknown environment.'
        data.update({
            'js_url': 'https://tppwscheckout-sandbox.e-id.nl/' + checkout_js,
            'js_environment': 'PostNL_OP_Checkout.environment_sandbox'
        })

    context['postnl_checkout'] = data

    return u''
