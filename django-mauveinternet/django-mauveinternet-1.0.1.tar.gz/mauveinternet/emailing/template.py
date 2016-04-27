import re

from django.conf import settings

from django.core.mail import EmailMessage
from django.template import loader, Template, Context, RequestContext, ContextPopException

def run_once(method):
    """Simple memoizing of accessor methods that take no arguments"""

    cache_prop = '__%s_cached' % method.func_name
    def wrapped(self):
        try:
            return getattr(self, cache_prop)
        except AttributeError:
            val = method(self)
            setattr(self, cache_prop, val)
            return val

    return wrapped


class BaseEmail(object):
    """An abstract e-mail templating class"""

    def generate(self, context):
        """Generate a tuple (subject, body, from) from the template using the context given.
        `from` may be None, in which case the Django DEFAULT_FROM_EMAIL setting will be used."""

    def to_email(self, recipients, args={}, context=None, bcc=[], headers={}):
        if context is None:
            context = Context({}, autoescape=False)

        context.update(args)
        subject, body, from_email = self.generate(context)
        context.pop()

#               if settings.DEBUG:
#                       bcc += [i[1] for i in settings.ADMINS]

        from_email = from_email or settings.DEFAULT_FROM_EMAIL

        return EmailMessage(subject=subject, body=body, from_email=from_email, to=recipients, bcc=bcc, headers=headers)


    def send_to(self, recipients, args={}, context=None, bcc=[], headers={}, attachments=[]):
        msg = self.to_email(recipients, args, context, bcc, headers=headers)
        for a in attachments:
            msg.attach_file(a)
        self.send(msg)

    def send(self, msg):
        if getattr(settings, 'LIVE_SERVER', True):
            msg.send()
        else:
            import mailbox
            mb = mailbox.mbox('debug_emails.mbox', create=True)
            mb.lock()
            mb.add(msg.message())
            mb.close()

    def send_to_all(self, recipient_tuples, args={}, context=None, bcc=[], attachments=[], headers={}):
        """For each `(email, recipient)` in recipient_tuples, generate and send an e-mail
        to `email` with `recipient` in the template context."""

        for email, recipient in recipient_tuples:
            rargs = {}
            rargs.update(args)
            rargs['recipient'] = recipient
            self.send_to([email], rargs, context=context, bcc=bcc, headers=headers, attachments=attachments)


class TemplateFileEmail(BaseEmail):
    """A templated e-mail in which a template to generate the e-mail is
    loaded from a file. The subject and body for the e-mail are
    parsed from the output which should be in an RFC822-like format."""

    HEADER_RE = re.compile(r'([\w-]+): (.*)')
    CONTINUATION_RE = re.compile(r'\s+(.*)')

    def __init__(self, template_file):
        super(TemplateFileEmail, self).__init__()
        self.template_file = template_file

    def get_template(self):
        return loader.get_template(self.template_file)

    def generate(self, context):
        template = self.get_template()
        email = template.render(context)

        # Simple parse of the generated email so that we can include subject and from in the templates
        headers = {}
        header_text, body = email.split('\n\n', 1)
        last_header = None
        for l in header_text.split('\n'):
            mo = self.HEADER_RE.match(l)
            if mo:
                headers[mo.group(1)] = mo.group(2)
                last_header = mo.group(1)
            else:
                mo = self.CONTINUATION_RE.match(l)
                if mo:
                    headers[last_header] += '\n' + mo.group(1)

        subject = headers['Subject']
        from_email = headers.get('From', None)

        return subject, body, from_email


class Email(BaseEmail):
    """A templated e-mail in which templates to generate the subject and body
    are passed in the constructor."""

    def __init__(self, sender, subject, body):
        """Construct an e-mail template. subject and body are in Django template format"""
        self.sender = sender
        self.subject = subject
        self.body = body

    def get_subject_template(self):
        return Template(self.subject)

    def get_body_template(self):
        return Template(self.body)

    def generate(self, context):
        subject = self.get_subject_template().render(context)
        body = self.get_body_template().render(context)

        return subject, body, self.sender
