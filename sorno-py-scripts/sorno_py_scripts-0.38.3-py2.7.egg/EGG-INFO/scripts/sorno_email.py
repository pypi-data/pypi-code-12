#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""Sends a simple email with plain text

The script first tries to use your system Mail Transfer Agent(MTA) configured,
otherwise, it prompts for login to use Gmail SMTP server.

The code is from
http://code4reference.com/2013/07/simple-python-script-to-send-an-email/


    Copyright 2015 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
from email.mime.text import MIMEText
import getpass
import logging
import smtplib
import socket
import sys

from sorno import loggingutil


_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class App(object):
    def __init__(
        self,
        args,
    ):
        """
        Args:
            args (argparse.Namespace): The flags for the script.
        """
        self.args = args

    def run(self):
        """The entry point of the script
        """
        email = MIMEText(self.args.msg)
        email['Subject'] = self.args.subject
        email['From'] = self.args.from_address
        email['to'] = self.args.to_address

        try:
            self.send_email_with_local_mta(email)
        except socket.error as e:
            _log.error("Failed to use MTA to send the email: %s", e)
            _log.info("Try Gmail SMTP server instead...")
            self.send_email_with_gmail(email)
        return 0

    def send_email_with_local_mta(self, email):
        """Sends email with your system Mail Transfer Agent(MTA) configured

        Args:
            email(MIMEText): The email object to be sent.

        Raises:
            socket.error if cannot connect to an SMTP locally
        """
        server = smtplib.SMTP("localhost")
        server.sendmail(
            self.args.from_address,
            self.args.to_address,
            email.as_string(),
        )
        server.quit()

    def send_email_with_gmail(self, email):
        """Sends email with Gmail SMTP server

        The method prompts the user to get the login information for the Gmail
        SMTP server from the terminal.

        Args:
            email(MIMEText): The email object to be sent.
        """
        smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        smtpserver.ehlo()
        # Put SMTP connection in TLS mode and call ehlo again.
        smtpserver.starttls()
        smtpserver.ehlo()
        # Login to service
        password = getpass.getpass(
            "Enter your password for %s to use Gmail SMTP server:" % (
                self.args.from_address
            )
        )
        smtpserver.login(
            user=self.args.from_address,
            password=password,
        )
        # Send email
        smtpserver.sendmail(
            self.args.from_address,
            self.args.to_address,
            email.as_string(),
        )
        # close connection and session.
        smtpserver.quit();


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2015")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--from",
        dest="from_address",
    )
    parser.add_argument(
        "--to",
        dest="to_address",
    )
    parser.add_argument(
        "--subject",
    )
    parser.add_argument(
        "--msg",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _plain_logger, _plain_error_logger

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)
    _plain_logger = loggingutil.create_plain_logger(
        "PLAIN",
        debug=args.debug,
    )
    _plain_error_logger = loggingutil.create_plain_logger(
        "PLAIN_ERROR",
        debug=args.debug,
        stdout=False,
    )

    app = App(
        args,
    )
    sys.exit(app.run())


if __name__ == '__main__':
    main()
