import koalasendgrid
import config
import unittest

__author__ = 'Matt'


class TestKoalaSendgrid(unittest.TestCase):
    def test_text_email(self):
        send_email_kwargs = {
            'to_address': config.secrets.get('test_email_to_email'),
            'subject': u'SendGrid API Test',
            'to_name': config.secrets.get('test_email_to_name'),
            'html': False,
            'body': 'This is a test email sent from SendGrid. Sendgrid is working correctly.'
        }
        response = koalasendgrid.send_email(**send_email_kwargs)
        self.assertEqual(200, response.status_code, u'Email failed to send')
