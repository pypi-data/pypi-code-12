import jinja2
import requests
from rssmailer.template import main_template

import logging
import sys
log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

class MailGun(object):
    '''send mail using mailgun.'''
    def __init__(self, api_key, mailgun_url, mail_to, mail_from,
                 title, content):
        self.api_key = api_key
        self.mailgun_url = mailgun_url
        self.mail_to = mail_to
        self.mail_from = mail_from
        self.title = title
        self.content = content
        self.template2 = jinja2.Environment().from_string(main_template)

    def build_html_message(self):
        self.output_text = self.template2.render(entries=self.content)

    def send_complex_message(self):
        try:
            requests.post(
                self.mailgun_url,
                auth=("api", self.api_key),
                data={"from": "RSS Digest Mailer " + self.mail_from,
                      "to": self.mail_to,
                      "subject": "Digest mail for " + self.title,
                      "html": self.output_text})
            return True
        except requests.exceptions.RequestException as e:
            log.error('Error sending mail for {} with error {}'.format(
                self.title, e))
            return False

    def send_complex_message_to_file(self):
        with open('test.html', 'w') as f:
            f.write(self.output_text)
