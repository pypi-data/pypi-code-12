'''
Created on Feb 10, 2016

@author: jivan
'''
from datetime import datetime
import logging

from django.shortcuts import render
from django.template.context import RequestContext
from django.views.generic import TemplateView

from confirmed_email.models import AddressConfirmation, QueuedEmailMessage
from django.conf import settings

ADDRESS_CONFIRMED_TEMPLATE = \
    getattr(settings, 'ADDRESS_CONFIRMED_TEMPLATE', 'confirmed_email/address_confirmed.html')


logger = logging.getLogger(__name__)


class HandleConfirmationClick(TemplateView):
    template_name = ADDRESS_CONFIRMED_TEMPLATE
    def get(self, request, uuid):
        # Mark the email associated with uuid as confirmed.
        ac = AddressConfirmation.objects.get(uuid=uuid)
        ac.confirmation_timestamp = datetime.now()
        ac.save()
        # Send any emails to this address which are waiting.
        send_queued_emails(ac)

        # Provide a page to thank the user for confirming.
        rc = RequestContext(request)
        rc.update({'email_address': ac.address})
        resp = render(request, self.template_name, rc)
        return resp


def send_queued_emails(address_confirmation):
    # Send queued emails for *address_confirmation*, provided the address has
    #    indeed been confirmed.
    # Afterwards send queued emails for any remaining to confirmed addresses.
    if address_confirmation.confirmation_timestamp:
        # queued emails
        qems = QueuedEmailMessage.objects.filter(address_confirmation=address_confirmation)
        for qem in qems:
            qem.send()
            qem.delete()
    else:
        logger.warn(
            'Attempt to send queued emails for unconfirmed address: {}'.format(address_confirmation)
        )

    # Check for and send queued emails for any destination addresses that have been confirmed.
    qems = QueuedEmailMessage.objects.filter(address_confirmation__confirmation_timestamp__isnull=False)
    for qem in qems:
        qem.send()
        qem.delete()
