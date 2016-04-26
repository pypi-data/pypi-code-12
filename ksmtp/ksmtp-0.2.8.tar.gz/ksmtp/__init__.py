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

  import ksmtp
  ksmtp.send(to="user@domain",
             subject="subject",
             body="some message")

  ksmtp.send(to="user@domain",
             subject="subject",
             body="some message",
             sender="user@domain",
             user="user",
             password="password",
             server="smtp.gmail.com",
             port="465",
             secure="ssl",
             debug=True)

Sample Config
=============

/etc/ksmtp.conf:

  [ksmtp]

  ## from email address
  from = username@gmail.com

  ## user
  user = username@gmail.com

  ## password
  pass = password

  ## server
  server = smtp.gmail.com

  ## port
  port = 465
  #port = 587

  ## secure
  secure = ssl
  #secure = tls


  ## default to email address (if none specified)
  #to = user@domain.com

  ## default catch-all (always CC)
  #catch-all = user@domain.com

  ## default subject
  #subject = default test subject

Issues
======

Gmail:
If you get an "smtplib.SMTPAuthenticationError" and your credentials are
correct, you may need to "allow less secure apps access" to your account.

See https://support.google.com/accounts/answer/6010255

"""

import smtplib
import email.mime.text
import os
import ConfigParser
# import re


CONF_FILE = '/etc/ksmtp.conf'
CONF_SECTION = 'ksmtp'


def _print_dict(conf):
    for key in conf:
        print key, '=', conf[key]


def _parse_config(conf):
    if os.path.exists(CONF_FILE):
        parser = ConfigParser.ConfigParser()
        parser.read(CONF_FILE)
        if parser.has_section(CONF_SECTION):
            if parser.has_option(CONF_SECTION, 'disabled'):
                conf["disabled"] = parser.get(CONF_SECTION, 'disabled')
            if parser.has_option(CONF_SECTION, 'to'):
                conf["to"] = parser.get(CONF_SECTION, 'to')
            if parser.has_option(CONF_SECTION, 'from'):
                conf["from"] = parser.get(CONF_SECTION, 'from')
            if parser.has_option(CONF_SECTION, 'catch-all'):
                conf["catch-all"] = parser.get(CONF_SECTION, 'catch-all')
            if parser.has_option(CONF_SECTION, 'user'):
                conf["user"] = parser.get(CONF_SECTION, 'user')
            if parser.has_option(CONF_SECTION, 'pass'):
                conf["pass"] = parser.get(CONF_SECTION, 'pass')
            if parser.has_option(CONF_SECTION, 'server'):
                conf["server"] = parser.get(CONF_SECTION, 'server')
            if parser.has_option(CONF_SECTION, 'port'):
                conf["port"] = parser.get(CONF_SECTION, 'port')
            if parser.has_option(CONF_SECTION, 'secure'):
                conf["secure"] = parser.get(CONF_SECTION, 'secure')
            if parser.has_option(CONF_SECTION, 'subject'):
                conf["subject"] = parser.get(CONF_SECTION, 'subject')
    return conf


def _validate_conf(conf):
    failure = None

    # validate to
    # if not re.match('[a-zA-Z0-9.-_]+@[a-zA-Z0-9.-_]+\.[a-zA-Z0-9.-_]+', conf["to"]):
    if not conf["to"]:
        failure = "Missing or invalid 'to' address"
    if "@" not in conf["to"]:
        conf["to"] = conf["to"] + "@localhost"

    # if not re.match('[a-zA-Z0-9.-_]+@[a-zA-Z0-9.-_]+\.[a-zA-Z0-9.-_]+', conf["from"]):
    #    failure = "Missing or invalid 'from' address"

    # if conf["catch-all"] and not re.match('[a-zA-Z0-9.-_]+@[a-zA-Z0-9.-_]+\.[a-zA-Z0-9.-_]+', conf["catch-all"]):
    #    failure = "Invalid 'catch-all' address"

    if conf["port"]:
        try:
            int(conf["port"])
        except:
            failure = "Invalid port number"

    if conf["secure"]:
        conf["secure"] = conf["secure"].lower()
        if conf["secure"] != 'ssl' and conf["secure"] != 'tls':
            failure = "Secure must be 'ssl' or 'tls'"

    # report on failure
    if failure:
        raise Exception("nError: %s!" % failure)


def send(to=None, subject=None, body=None,
         sender=None, user=None, password=None, server=None, port=None, secure=None, debug=None):
    """
    Example:

      send(to="user@domain",
         sender="user@domain",
         subject="subject",
         body="some message",
         user="user",
         password="password",
         server="smtp.gmail.com",
         port="465",
         secure="ssl",
         debug=True)
    """

    # Configuration options
    conf = {}
    conf["to"] = None               # user@domain.com - to address
    conf["from"] = None             # user@domain.com - from address
    conf["catch-all"] = None        # user@domain.com - send all mail to override
    conf["user"] = None             # username
    conf["pass"] = None             # password
    conf["server"] = 'localhost'    # localhost / smtp.gmail.com
    conf["port"] = 25               # 25 / 587 (tls) / 465 (ssl)
    conf["secure"] = False          # tls / ssl
    conf["subject"] = ''            # '' - default subject
    conf["debug"] = False         # debug output

    conf = _parse_config(conf)
    if "disabled" in conf and conf["disabled"] == "true":
        raise Exception("Error: see /etc/ksmtp.conf configuration file!")
    if to:
        conf["to"] = to
    if subject:
        conf["subject"] = subject
    if sender:
        conf["from"] = sender  # "from" is python keyword
    if user:
        conf["user"] = user
    if password:
        conf["password"] = password
    if server:
        conf["server"] = server
    if port:
        conf["port"] = port
    if secure:
        conf["secure"] = secure
    if debug:
        conf["debug"] = debug
    _validate_conf(conf)

    debug = conf["debug"]
    if debug:
        print "Configuration:"
        _print_dict(conf)
        print "-"

    msg = email.mime.text.MIMEText(body)

    if conf["subject"]:
        msg['Subject'] = conf["subject"]
    if conf["from"]:
        msg['From'] = conf["from"]
    if conf["to"]:
        msg['To'] = conf["to"]
        # msg['To'] = ", ".join(to_emails)

    if conf["secure"] == "ssl":
        if debug:
            print "Connecting to %s:%s over SSL ..." % (conf["server"], conf["port"])
        s = smtplib.SMTP_SSL(conf["server"], conf["port"])
    else:
        if debug:
            print "Connecting to %s:%s..." % (conf["server"], conf["port"])
        s = smtplib.SMTP(conf["server"], conf["port"])
        if conf["secure"] == "tls":
            s.ehlo()
            if debug:
                print "Starting TLS ..."
            s.starttls()
            s.ehlo()
    if conf["user"] and conf["pass"]:
        if debug:
            print "Logging in as %s ..." % conf["user"]
        s.login(conf["user"], conf["pass"])

    if conf["catch-all"]:
        if debug:
            print "Sending message to forced %s ..." % conf["catch-all"]
        s.sendmail(conf["from"], [conf["catch-all"]], msg.as_string())
    else:
        if debug:
            print "Sending message to %s ..." % conf["to"]
        s.sendmail(conf["from"], [conf["to"]], msg.as_string())
    if debug:
        print "Message Sent."

    if debug:
        print "Quitting ..."
    s.quit()


if __name__ == '__main__':
    pass
