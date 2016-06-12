# -*- coding: utf-8 -*-

import asyncore, email.mime.text, smtpd, smtplib

class server (smtpd.SMTPServer):

    def process_message (self, address, sender, recipient, message):
        server.address = address
        server.sender = sender
        server.recipient = recipient
        server.message = message
        print server.message

def listen (port):
    server(("0.0.0.0", port), None)
    asyncore.loop()

def send (address, sender, recipient, subject, content):
    """Send MIME message from string."""
    smtp = smtplib.SMTP(address)
    mime = email.mime.text.MIMEText(content)
    mime["From"] = sender
    mime["To"] = recipient
    mime["Subject"] = subject
    smtp.sendmail(sender, recipient, mime.as_string())
    smtp.quit()