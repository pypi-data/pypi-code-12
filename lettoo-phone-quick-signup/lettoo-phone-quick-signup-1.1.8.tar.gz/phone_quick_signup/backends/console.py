# -*- coding: utf-8 -*-
"""
SMS backend that writes messages to console instead of sending them.

This is a total ripoff of django.core.mail.backends.console
"""
import sys
import threading

from .base import BaseSmsBackend


class SmsBackend(BaseSmsBackend):
    def __init__(self, *args, **kwargs):
        self.stream = kwargs.pop('stream', sys.stdout)
        self._lock = threading.RLock()
        super(SmsBackend, self).__init__(*args, **kwargs)

    def send_messages(self, messages):
        """Write all messages to the stream in a thread-safe way."""
        if not messages:
            return 0
        self._lock.acquire()
        try:
            try:
                stream_created = self.open()
                for message in messages:
                    self.stream.write(render_message(message))
                    self.stream.write('\n')
                    self.stream.write('-' * 79)
                    self.stream.write('\n')
                    self.stream.flush()  # flush after each message
                if stream_created:
                    self.close()
            except:
                if not self.fail_silently:
                    raise
        finally:
            self._lock.release()
        return len(messages)


def render_message(message):
    return u"""from: %(from)s\nto: %(to)s\n%(body)s""" % {
        'from': message['from_phone'],
        'to': ", ".join(message['to']),
        'body': message['body'] % message['params'],
    }
