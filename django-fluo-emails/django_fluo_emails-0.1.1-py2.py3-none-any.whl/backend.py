# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# EmailBackend adapted from https://github.com/stefanfoulis/django-database-email-backend
# Copyright (C) 2011 Stefan Foulis and contributors.

from __future__ import absolute_import, division, print_function, unicode_literals
import sys
import threading
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.encoding import smart_text
from django.utils import six
from django.utils.six.moves.email_mime_base import MIMEBase
from .models import Email, Attachment


class EmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()
        super(EmailBackend, self).__init__(*args, **kwargs)

    def _write_message(self, message):
        msg = message.message()
        if six.PY3:
            msg_data = msg.as_bytes()
            charset = msg.get_charset().get_output_charset() if msg.get_charset() else 'utf-8'
            msg_data = msg_data.decode(charset)
        else:
            msg_data = smart_text(msg.as_string())
        self.stream.write('%s\n' % msg_data)
        self.stream.write('-' * 79)
        self.stream.write('\n')
        self.stream.flush()  # flush after each message

    def _save_on_db(self, message):
        email = Email.objects.create(
            from_email='%s' % message.from_email,
            to_emails=', '.join(message.to),
            cc_emails=', '.join(message.cc),
            bcc_emails=', '.join(message.bcc),
            all_recipients=', '.join(message.recipients()),
            subject=message.subject,
            body=message.body,
            raw='%s' % smart_text(message.message().as_string()),
        )
        for attachment in message.attachments:
            if isinstance(attachment, tuple):
                filename, content, mimetype = attachment
            elif isinstance(attachment, MIMEBase):
                filename = attachment.get_filename()
                content = attachment.get_payload(decode=True)
                mimetype = None
            else:
                continue
            Attachment.objects.create(
                email=email,
                filename=filename,
                content=content,
                mimetype=mimetype
            )

    def send_messages(self, email_messages):
        if not email_messages:
            return

        # for console
        with self._lock:
            try:
                stream_created = self.open()
                for message in email_messages:
                    self._save_on_db(message)
                    try:
                        self._write_message(message)
                    except:
                        pass
                if stream_created:
                    self.close()
            except:
                if not self.fail_silently:
                    raise

        return len(email_messages)
