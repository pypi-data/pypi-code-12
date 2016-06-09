'''
Created on Feb 10, 2016

@author: jivan
'''
import copy
from django.core.mail.message import EmailMultiAlternatives
from confirmed_email.models import AddressConfirmation, QueuedEmailMessage
import logging
logger = logging.getLogger(__name__)

def send_mail_confirmed(subject, message, from_email, recipient_list,
        fail_silently=False, auth_user=None, auth_password=None,
        connection=None, html_message=None
    ):
    from django.core.mail import get_connection
    connection = connection or get_connection(username=auth_user,
                                    password=auth_password,
                                    fail_silently=fail_silently)
    return ConfirmedEmailMessage(subject, message, from_email, recipient_list,
                        connection=connection).send()

class ConfirmedEmailMessage(EmailMultiAlternatives):
    def send(self, *args, **kwargs):
        ''' | *brief*: Sends message, preceding it with a confirmation email or
            |    unconfirmed addresses.
            | *author*: Jivan
            | *created*: 2016-02-23
            In the parent's send() the return value is the number of email messages
            processed which would be 0 (for failure) or 1 (for success).

            This class returns a dictionary with all recipient
            addresses as keys and the text 'sent', 'queued', or
            'failed' as the value
            for each key.
        '''
        destination_count = len(self.recipients())
        confirmed = AddressConfirmation.objects.filter(
                        address__in=self.recipients(),
                        confirmation_timestamp__isnull=False)
        confirmed_addresses = [ c.address for c in confirmed ]
        confirmed_count = len(confirmed_addresses)

        send_results = {}
        # If all the destination addresses are confirmed, send as-is.
        if destination_count == confirmed_count:
            if super(ConfirmedEmailMessage, self).send():
                send_results.update({ ca: 'sent' for ca in confirmed_addresses })
        else:
            # If any of the destination addresses are unconfirmed, send to
            #    each individually.
            for recipient in self.recipients():
                cem = ConfirmedEmailMessage(
                    self.subject, self.body, self.from_email,
                    connection=self.connection, attachments=self.attachments,
                    headers=self.extra_headers, alternatives=self.alternatives
                )
                cem.to = [recipient]
                cem.cc = []
                cem.bcc = []
                if recipient in confirmed_addresses:
                    single_send_result = cem.send()
                    send_results.update(single_send_result)
                else:
                    # sending_results is the number of messages sent.
                    sending_result = cem._send_unconfirmed()
                    if sending_result:
                        send_results.update({recipient: 'queued'})
                    else:
                        send_results.update({recipient: 'failed'})

        return send_results

    def _send_unconfirmed(self):
        ''' | *brief*: Queues this message for later delivery and sends a confirmation
            |     message to the recipient.
            | *note*: Only single-recipient messages are allowed.
            *returns*: 0 if sending confirmation message failed, 1 if sending
                confirmation message succeeded.
        '''
        if len(self.recipients()) > 1:
            msg = '_send_unconfirmed() should not be used directly.  Use send().'
            logger.error(msg)
        address = self.recipients()[0]

        # Add address to EmailAddresses
        ac = AddressConfirmation.objects.get_or_create(address=address)[0]
        # Queue message
        qem = QueuedEmailMessage.objects.create(address_confirmation=ac, email_contents=self)
        if not qem:
            logger.error('Unable to create QueuedEmailMessage to {}'.format(address))
        # Send confirmation email
        confirmation_message_error = ac.send_confirmation_request(from_address=self.from_email)
        return confirmation_message_error

    def __eq__(self, other):
        # Assume equal
        equal = True

        # If the number of attachments differs, not equal
        if len(self.attachments) != len(other.attachments):
            equal = False

        # If the properties differ, not equal
        if equal and (self.__dict__ != other.__dict__):
            equal = False

        # If the attachments differ, not equal
        if equal:
            for at1, at2 in zip(self.attachments, other.attachments):
                if at1 != at2:
                    equal = False
                    break
        return equal

    def __unicode__(self):
        u = u''
        for key, val in self.__dict__.items():
            u += '{}: {}\n'.format(key, val)
        return u

    def __getstate__(self):
        d = dict(self.__dict__)
        del d['connection']
        return d

    def __setstate__(self, d):
        self.__dict__.update(d)
        self.connection = False
