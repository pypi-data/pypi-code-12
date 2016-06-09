'''
Created on Feb 10, 2016

@author: jivan
'''
import base64
import cPickle
from cStringIO import StringIO
from datetime import date
import uuid

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.shortcuts import render
from django.template.loader import render_to_string


# Collect the number of days between confirmation emails from settings.
#    Default to 3 if it's not provided.
EMAIL_CONFIRMATION_WAIT = settings.__dict__.get('EMAIL_CONFIRMATION_WAIT', 3)
EMAIL_CONFIRMATION_TEMPLATE_TXT = \
    getattr(settings, 'EMAIL_CONFIRMATION_TEMPLATE_TXT', 'confirmed_email/confirmation_email.txt')
EMAIL_CONFIRMATION_TEMPLATE_HTML = \
    getattr(settings, 'EMAIL_CONFIRMATION_TEMPLATE_HTML', 'confirmed_email/confirmation_email.html')

class AddressConfirmation(models.Model):
    ''' Stores addresses with their confirmation status. '''
    address = models.EmailField()
    # unique string used as part of the confirmation link.
    uuid = models.CharField(max_length=32, default=uuid.uuid1)
    # This is None for unconfirmed addresses or the timestamp when the user clicked
    #    the confirmation link.
    confirmation_timestamp = models.DateTimeField(null=True)
    last_request_date = models.DateField(null=True)
    request_count = models.IntegerField(default=0)

    def send_confirmation_request(self, from_address):
        ''' | *brief*: Sends an email requesting that *from_address* be confirmed.
            | *author*: Jivan
            | *created*: 2016-03-02
            Sends an email if one hasn't been sent in more than EMAIL_CONFIRMATION_WAIT days.
            Like EmailMessage, returns 0 for an email sending failure, 1 for sending success.
            A value of 1 is also returned for a message skipped due to a previous message
            sent within EMAIL_CONFIRMATION_WAIT days.
        '''
        if self.last_request_date is None:
            days_since_request = None
        else:
            delta = date.today() - self.last_request_date
            days_since_request = delta.days

        ret = 1
        if days_since_request is None or days_since_request > EMAIL_CONFIRMATION_WAIT:
            current_domain = Site.objects.get_current().domain

            confirmation_location = \
                reverse('confirmed-email-confirmation-url', kwargs={'uuid': self.uuid})
            confirmation_link = 'http://' + current_domain + confirmation_location
            message_context = {'confirmation_link': confirmation_link}
            message_body_text = render_to_string(EMAIL_CONFIRMATION_TEMPLATE_TXT, message_context)
            message_body_html = render_to_string(EMAIL_CONFIRMATION_TEMPLATE_HTML, message_context)

            # Confirmation Email
            em = EmailMultiAlternatives(subject='Please confirm your email address',
                              body=message_body_text,
                              from_email=from_address,
                              to=[self.address])
            em.attach_alternative(message_body_html, "text/html")

            ret = em.send()
            if ret:
                self.last_request_date = date.today()
                self.save()

        return ret


class QueuedEmailMessage(models.Model):
    ''' Stores unsent email messages while waiting for confirmation.'''
    address_confirmation = models.ForeignKey(AddressConfirmation)
    # Date when the message was queued while awaiting confirmation.
    date = models.DateField(auto_now=True)
    # ConfirmedEmailMessage instance serialized with json-pickle.
    _email_contents = models.TextField(db_column='email_contents', blank=True)

    @property
    def email_contents(self):
        # --- Decode & unpickle the message
        pickle_input = base64.decodestring(self._email_contents)
        # In-memory pickle input
        pi = StringIO(pickle_input)
        message = cPickle.load(pi)

        return message

    @email_contents.setter
    def email_contents(self, email_message):
        # --- Pickle & encode the message for storage in a TextField.
        # In-memory pickle output.
        po = StringIO()
        cPickle.dump(email_message, po)
        pickle_output = po.getvalue()
        po.close()

        self._email_contents = base64.encodestring(pickle_output)

    def send(self):
        res = self.email_contents.send()
        return res
