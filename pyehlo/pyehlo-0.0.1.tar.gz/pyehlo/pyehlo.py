import smtplib
import contextlib
import email.mime.text as text

TARGETS = ['me@example.com']


class MailClientBase:

    def __init__(self):
        pass

    def send(self):
        raise NotImplementedError()


class GmailClient(MailClientBase):

    HOST_AND_PORT = "smtp.gmail.com:587"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.server = smtplib.SMTP(GmailClient.HOST_AND_PORT)

    @contextlib.contextmanager
    def login(self):
        self.server.ehlo()
        self.server.starttls()
        self.server.login(self.username, self.password)
        yield
        self.server.quit()

    def send(self, target, message, subject='', from_name=None):
        if from_name is None:
            from_name = self.username
        msg = text.MIMEText(message)
        msg['Subject'] = subject
        msg['From'] = from_name
        msg['To'] = target
        self.server.send_message(msg)
