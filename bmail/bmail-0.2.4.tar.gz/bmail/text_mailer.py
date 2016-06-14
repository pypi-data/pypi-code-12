
import sys, smtplib, traceback
from email.mime.text import MIMEText
from bl.dict import Dict
from bl.log import Log

class TextMailer(Dict):
    """create and send text email using templates. Parameters (*=required):
        template*       : must have a render() method that takes keyword arguments
                            (if loader_class and TextMailer.template_path are both given, 
                                template can be a relative path)
        loader_class    : the class used to load templates (defaults to tornado.template.Loader).
        Email           : parameters from the Email config.
            template_path: the filesystem location in which to search for templates
            host        : The address of the mail host
            port        : The port the host is listening on
            from_address: The default From address
            to_address  : The default To address
            delivery    : 'smtp' sends it, 'test' returns the rendered message 
            username    : username for smtp auth
            password    : password for smtp auth
            debug       : Whether debugging is on
    """

    def __init__(self, loader_class=None, loader_args={}, log=Log(), **Email):
        """set up an emailer with a particular Email config"""
        Dict.__init__(self, log=log, **Email)
        if loader_class is None:
            from tornado.template import Loader as loader_class
        if Email.get('template_path') is not None:
            self.loader = loader_class(Email.get('template_path'), **loader_args)
        if self.delivery=='test' and self.default_encoding is None:
            self.default_encoding = 'ASCII'
        else:
            self.default_encoding = 'UTF-8'

    def __repr__(self):
        return "Emailer(%r)" % (self.__file__)

    def render(self, template, **context):
        """render the emailer template with the given context."""
        if type(template)==str and self.loader is not None:
            template = self.loader.load(template)
        try:
            r = template.render(**context)
        except:
            r = template.generate(**context)
        if type(r)==type(b''): r = r.decode('UTF-8')
        return r

    def message(self, template=None, text=None, to_addr=None, subject=None, from_addr=None, cc=None, bcc=None, encoding=None, **context):
        """create a MIMEText message from the msg text with the given msg args"""
        encoding = encoding or self.default_encoding or 'UTF-8'
        if template is not None:
            text = self.render(template, to_addr=to_addr or self.to_address, from_addr=from_addr, cc=cc, bcc=bcc, **context)
        msg = MIMEText(text, 'plain', encoding)
        msg['From'] = from_addr or self.from_address
        msg['Subject'] = subject
        for addr in [addr for addr in (to_addr or self.to_address or '').split(',') if addr.strip() != '']:
            msg.add_header('To', addr.strip())
        for addr in [addr for addr in (cc or '').split(',') if addr.strip() != '']:
            msg.add_header('Cc', addr.strip())
        for addr in [addr for addr in (bcc or '').split(',') if addr.strip() != '']:
            msg.add_header('Bcc', addr.strip())
        return msg

    def send_message(self, template, to_addr=None, subject=None, from_addr=None, cc=None, bcc=None, **context):
        return self.send(
            self.message(template,
                to_addr=to_addr, from_addr=from_addr, cc=cc, bcc=bcc, subject=subject, **context))

    def send(self, msg):
        """send the given msg and return the status of the delivery.
        Returns None if delivery succeeded.
        Returns a sys.exc_info() tuple if the SMPT client raised an exception.
        """
        if self.delivery == 'test':
            # return the message as text that would be sent
            return msg.as_string()

        elif self.delivery == 'smtp':
            # parse the message and send it
            fromaddr = msg['From']
            if self.debug==True: self.log("From =", fromaddr)
            tolist = [addr for addr in
                      (msg.get_all('To') or []) 
                      + (msg.get_all('Cc') or []) 
                      + (msg.get_all('Bcc') or [])
                      if addr is not None and addr.strip() != '']
            try:
                if self.port is not None:
                    smtpclient = smtplib.SMTP(self.host or '127.0.0.1', self.port)
                else:
                    smtpclient = smtplib.SMTP(self.host or '127.0.0.1')
                smtpclient.set_debuglevel(self.debug and 1 or 0)    # non-zero gives us exceptions when emailing.
                if self.username is not None and self.password is not None:
                    smtpclient.login(self.username, self.password)
                for toaddr in tolist:
                    if self.debug==True: self.log("To =", toaddr)
                    smtpclient.sendmail(fromaddr, toaddr, msg.as_string())
                smtpclient.quit()
            except:
                if self.debug==True: 
                    self.log(traceback.format_exc())
                else:
                    self.log("Emailer exception:", sys.exc_info()[1], file=sys.stderr)
                return sys.exc_info()[1]        # return the exception rather than raising it -- the show must go on.        
