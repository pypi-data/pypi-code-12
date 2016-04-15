
try:
    import unittest.mock as mock
except:
    import mock

import simple_mail as mail

from templated_mail.message_loader import MessageLoader
from templated_mail.sub_template_loader import SubTemplateLoader


class TemplatedMail(object):

    def __init__(self, config, logger=None):
        """
        Store config for the mail server,
        and the location of email templates.

        """

        self.config = config
        self.logger = logger if logger is not None else mock.Mock()
        self.mail = mail.Mail(config)
        self.loader = MessageLoader(config, self.logger)

    def send_message(self, name, recipients, context=None,
                     reply_to=None, cc=None, bcc=None):
        """
            1) Build the email template of `name`, as found
            under the configured message directory.
            2) Load and render the subject, text and HTML,
            as defined in <MESSAGE_DIR>/use_my_service.msg,
            with the given context.

        """

        msg = self.loader.get_message(name)
        if msg is not None:
            values = msg.render(**context)
            self.mail.send_message(
                values.subject,
                recipients,
                values.body,
                values.html,
                reply_to=reply_to,
                cc=cc, bcc=bcc
            )

        else:
            self.logger.error('couldn\'t render a template.')
