import argparse
import base64
import datetime
import re
import sys
from os import path
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import pkg_resources


class Gmail:

    PACKAGE_NAME = 'cutils'
    SCOPES = 'https://mail.google.com/'
    CLIENT_SECRET_FILE = pkg_resources.resource_filename(PACKAGE_NAME, 'fattywhitysmarty.json')
    APPLICATION_NAME = 'Notifier'

    def __init__(self, minDuration=3600*24):
        self._flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args([])
        self._create_at = datetime.datetime.now()
        self._min_duration = minDuration
        self._subject = 'AWS Status'
        self._message_text = '\n'
        self._credentials_file = './fattywhitysmarty.credentials'

    def get_credentials(self):
        # if self._credentials_file != '.':
        credentials_file = self._credentials_file
        # credentials_file = pkg_resources.resource_filename(self.PACKAGE_NAME, re.sub('@.+$', '', self._sender) + '.credentials')
        store = file.Storage(credentials_file)
        credentials = store.get()
        if not credentials or credentials.invalid:
            try:
                flow = client.flow_from_clientsecrets(self.CLIENT_SECRET_FILE, self.SCOPES)
                flow.user_agent = self.APPLICATION_NAME
                if self._flags:
                    credentials = tools.run_flow(flow, store, self._flags)
                else:  # Needed only for compatability with Python 2.6
                    credentials = tools.run(flow, store)
                    # print 'Storing credentials to ' + credential_path
            except IOError:
                print 'Credential file needs updating.'
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
        if (datetime.datetime.now() - self._create_at).seconds <= self._min_duration or self._min_duration == 0:
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

    def set_credentials(self, credential_fp='.'):
        if '.credentials' in credential_fp:
            self._credentials_file = credential_fp
        else:
            self._credentials_file = path.join(credential_fp, 'fattywhitysmarty.credentials')
        return self

# test
# g = Gmail(minDuration=10).set_from_to().set_subject('test')
# g = g.send_message('a')
# g = g.close()
