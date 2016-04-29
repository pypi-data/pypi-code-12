import argparse
import base64
import datetime
import re
import sys
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools

# sys.path.extend(['./cutils/'])


class Gmail:

    SCOPES = 'https://mail.google.com/'
    CLIENT_SECRET_FILE = 'cutils/fattywhitysmarty_json.py'
    APPLICATION_NAME = 'Notifier'

    _message_text = ''

    def __init__(self, minDuration=3600*24):
        self._flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args([])
        self._create_at = datetime.datetime.now()
        self._min_duration = minDuration
        self._subject = 'AWS Status'

    def get_credentials(self):
        credential_file = 'cutils/' + re.sub('@.+$', '', self._sender) + '_credentials.py'
        store = file.Storage(credential_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
            flow.user_agent = self.APPLICATION_NAME
            if self._flags:
                credentials = tools.run_flow(flow, store, self._flags)
            else:  # Needed only for compatability with Python 2.6
                credentials = tools.run(flow, store)
                # print 'Storing credentials to ' + credential_path
        return credentials

    @staticmethod
    def create_message(sender, to, subject, message_text):
        message = MIMEText(message_text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.b64encode(message.as_string())}

    def send_message(self, message_text):
        self._credentials = self.get_credentials()
        self._service = build('gmail', 'v1', http=self._credentials.authorize(Http()))
        self._message_text += message_text + ' '
        if (datetime.datetime.now() - self._create_at).seconds <= self._min_duration:
            return self
        else:
            message = self.create_message(self._sender + '@gmail.com', self._receiver, self._subject, self._message_text)
            self._service.users().messages().send(userId='me', body=message).execute()
            self._message_text = ''
            self._create_at = datetime.datetime.now()
            return self

    def close(self):
        message = self.create_message(self._sender + '@gmail.com', self._receiver, self._subject, self._message_text)
        self._service.users().messages().send(userId='me', body=message).execute()
        self._message_text = ''
        self._create_at = datetime.datetime.now()
        return self

    def set_from_to(self, sender='fattywhitysmarty', receiver='fattywhitysmarty'):
        if '@' not in sender:
            self._sender = sender + '@gmail.com'
        else:
            self._sender = sender
        if '@' not in receiver:
            self._receiver = receiver + '@gmail.com'
        else:
            self._receiver = receiver
        return self

    def set_subject(self, subject):
        self._subject = subject
        return self

    def set_min_duration(self, minDuration):
        self._min_duration = minDuration
        return self

# test
# g = Gmail(minDuration=10).set_from_to().set_subject('test')
# g = g.send_message('a')
# g = g.close()


