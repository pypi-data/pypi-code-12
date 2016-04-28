"""

This module is a little hack mostly using code
from https://github.com/wilbertom/ayu/blob/master/ayu/emails.py, that
patches the email functions we once used in a flask app.

It has since been adapted for more general use in email-sending.

"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from datetime import datetime
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


DEFAULT_CODEC = 'utf-8'


EMAIL_LOG = \
    """
    --------------------------
    Time: {}
    writing email to: '{}'
    with subj: '{}'
    --------------------------
    """

SUPPRESS_LOG = \
    """
    *********************
    DID NOT send an email
    Here is how it would have looked:
    **********************
    """


class DefaultConfig(object):

    # MUST be re-defined
    EMAIL_ADDRESS = None
    EMAIL_PASSWORD = None
    MAIL_HOST = ''
    MAIL_PORT = 0

    # May be defined, or changed
    NAME = None
    REPLY_TO = None
    DEBUG = True
    SUPPRESS = False


class Mail(object):

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger if logger is not None else Mock()

    def server(self, email, password):
        server = smtplib.SMTP_SSL(self.config.MAIL_HOST, self.config.MAIL_PORT)
        server.set_debuglevel(self.config.DEBUG)
        server.ehlo()
        server.login(email, password)

        return server

    @staticmethod
    def new_email(fr, to, subject, body, html, reply_to=None,
                  cc=None, bcc=None):

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject.encode(DEFAULT_CODEC, errors='replace')
        msg['To'] = to.encode(DEFAULT_CODEC, errors='replace')
        msg['From'] = fr.encode(DEFAULT_CODEC, errors='replace')

        if reply_to is not None:
            msg['Reply-To'] = reply_to.encode(DEFAULT_CODEC, errors='replace')

        if cc is not None:
            msg['Cc'] = cc.encode(DEFAULT_CODEC, errors='replace')

        if bcc is not None:
            msg['Bcc'] = bcc.encode(DEFAULT_CODEC, errors='replace')

        part_text = MIMEText(
            body.encode(DEFAULT_CODEC, errors='replace'),
            'text', _charset=DEFAULT_CODEC
        )
        part_html = MIMEText(
            html.encode(DEFAULT_CODEC, errors='replace'),
            'html', _charset=DEFAULT_CODEC
        )

        msg.attach(part_text)
        msg.attach(part_html)

        return msg

    def send_message(self, subject, recipients, body, html, *args, **kwargs):

        """
        Compatible with the send_message
        method of Flask-Mail.

        """

        if self.config.NAME is None:
            from_address = self.config.EMAIL_ADDRESS
        else:
            from_address = formataddr((
                self.config.NAME,
                self.config.EMAIL_ADDRESS
            ))
        from_address.encode(DEFAULT_CODEC,
                            errors='replace')

        to_addresses = '; '.join(recipients) if \
            len(recipients) > 1 else recipients[0]
        to_addresses.encode(DEFAULT_CODEC,
                            errors='replace')

        email_log = EMAIL_LOG.format(
            datetime.utcnow(),
            to_addresses,
            subject
        )

        if self.config.SUPPRESS:
            self.logger.info(SUPPRESS_LOG + email_log)

        else:

            self.logger.info(email_log)
            email = self.new_email(
                from_address,
                to_addresses,
                subject, body, html,
                reply_to=kwargs.get('reply_to') or \
                         self.config.REPLY_TO,
                cc=kwargs.get('cc'),
                bcc=kwargs.get('bcc')
            )

            try:
                server = self.server(
                    self.config.EMAIL_ADDRESS,
                    self.config.EMAIL_PASSWORD
                )
                server.sendmail(
                    from_address,
                    to_addresses,
                    email.as_string()
                )
            except smtplib.SMTPException as e:
                self.logger.error(
                    'Time: {}; got an SMTP error: {}'.format(
                        datetime.utcnow(), e
                ))
                raise e
