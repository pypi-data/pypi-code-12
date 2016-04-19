"""

ksmtp - Simple Python SMTP relay replacement for sendmail with SSL authentication


ksmtp
=====

Simple Python SMTP relay replacement for sendmail with SSL authentication

Useful for relaying all email through an account like Gmail, without the
messy configurations of Postfix / Sendmail.

Source
======

PyPI - https://pypi.python.org/pypi/ksmtp
GitHub - https://github.com/oeey/ksmtp

Usage
=====

  1) pip install ksmtp
  2) edit /etc/ksmtp.conf with your login credentials
  3) (optional) create symlink to ksmtp to replace sendmail
     ln -s `which ksmtp` /usr/sbin/sendmail
  4) send test mail
     ksmtp test@test.com -s "some subject"

Issues
======

Gmail:
If you get an "smtplib.SMTPAuthenticationError" and your credentials are
correct, you may need to "allow less secure apps access" to your account.

See https://support.google.com/accounts/answer/6010255

"""
