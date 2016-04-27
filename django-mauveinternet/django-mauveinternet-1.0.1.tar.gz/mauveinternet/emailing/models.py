from django.conf import settings
from django.db import models

from django.core.mail import EmailMessage
from django.template import Template, Context, RequestContext, ContextPopException

from template import BaseEmail

class TemplateEmail(models.Model, BaseEmail):
    slug = models.SlugField('Internal name for referencing this e-mail', editable=False)
    sender = models.EmailField()

    subject = models.CharField("Django template for generating the subject", max_length=255)
    body = models.TextField("Django template for generating the body")

    def __unicode__(self):
        return self.slug

    class Admin:
        list_display = ['slug', 'sender', 'subject']

    class Meta:
        verbose_name = u'e-mail template'

    def get_subject_template(self):
        return Template(self.subject)

    def get_body_template(self):
        return Template(self.body)

    def generate(self, context):
        subject = self.get_subject_template().render(context)
        body = self.get_body_template().render(context)

        return subject, body, self.sender

    @staticmethod
    def get(slug, sender, subject, body):
        """Shortcut method for retrieving a TemplateEmail from the database, using the defaults given if it doesn't exist."""

        try:
            return TemplateEmail.objects.get(slug=slug)
        except TemplateEmail.DoesNotExist:
            return TemplateEmail(slug=slug, sender=sender, subject=subject, body=body)
