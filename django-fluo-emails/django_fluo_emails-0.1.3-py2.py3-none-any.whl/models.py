# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Email/Attachment adapted from https://github.com/stefanfoulis/django-database-email-backend
# Copyright (C) 2011 Stefan Foulis and contributors.

from __future__ import absolute_import, division, print_function, unicode_literals
from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives
from django.template import Template, RequestContext, Context
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.utils import six
from django.contrib.sites.models import Site
from fluo.db import models


def _get_default_from_email():
    return settings.DEFAULT_FROM_EMAIL


class EmailTemplateQuerySet(models.QuerySet):
    pass


class EmailTemplateManager(models.Manager.from_queryset(EmailTemplateQuerySet)):
    use_for_related_fields = True

    def send(self, name, **kwargs):
        mail = self.get(name=name)
        return mail.send(**kwargs)


@python_2_unicode_compatible
class EmailTemplate(models.TimestampModel, models.I18NModel):
    objects = EmailTemplateManager()

    from_email = models.CharField(
        max_length=255,
        default=_get_default_from_email,
        verbose_name=_('from email'),
    )
    default_to = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('default to'),
        help_text=_('comma separated value'),
    )
    default_cc = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('default cc'),
        help_text=_('comma separated value'),
    )
    default_bcc = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('default bcc'),
        help_text=_('comma separated value'),
    )
    default_reply_to = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('default reply_to'),
        help_text=_('comma separated value'),
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        verbose_name=_('name'),
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('subject'),
    )
    body = models.TextField(
        verbose_name=_('body'),
    )
    body_html = models.TextField(
        blank=True,
        default='',
        verbose_name=_('html body'),
    )
    noreply = models.BooleanField(
        default=False,
        verbose_name=_("no reply"),
        help_text=_("should add a Reply-to with noreply@domain header"),
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("notes"),
    )

    class Meta:
        ordering = ['name']
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')

    def __str__(self):
        return self.name

    def create(self, request=None, from_email=None, to=None, cc=None, bcc=None, reply_to=None, context=None, attachments=None, alternatives=None, fail_silently=True, auth_user=None, auth_password=None, connection=None, headers=None, noreply=False, language=None, subject=None, body=None):
        site = Site.objects.get_current()
        subject_template = Template(self.translate(language=language).subject if subject is None else subject)
        body_template = Template(self.translate(language=language).body if body is None else body)

        context = {} if context is None else context
        context = Context(context) if request is None else RequestContext(request, context)

        connection = connection or get_connection(
            username=auth_user,
            password=auth_password,
            fail_silently=fail_silently,
        )

        if isinstance(to, six.string_types):
            to = [ to ]
        elif self.default_to:
            to = self.default_to.split(',')
        if isinstance(cc, six.string_types):
            cc = [ cc ]
        elif self.default_cc:
            cc = self.default_cc.split(',')
        if isinstance(bcc, six.string_types):
            bcc = [ bcc ]
        elif self.default_bcc:
            bcc = self.default_bcc.split(',')
        if isinstance(reply_to, six.string_types):
            reply_to = [ reply_to ]
        elif self.default_reply_to:
            reply_to = self.default_reply_to.split(',')

        headers = headers = {} if headers is None else headers
        noreply = noreply or self.noreply
        if noreply and not reply_to and 'Reply-to' not in headers:
            reply_to = ['noreply@%s' % site.domain]

        kwargs = {
            'subject': subject_template.render(context).replace("\n", ""),
            'body': body_template.render(context),
            'from_email': self.from_email if from_email is None else from_email,
            'to': to,
            'cc': cc,
            'bcc': bcc,
            'reply_to': reply_to,
            'headers': headers,
            'connection': connection,
            'attachments': attachments,
            'alternatives': alternatives,
        }

        email = EmailMultiAlternatives(**kwargs)
        if self.body_html:
            body_html_template = Template(self.translate(language=language).body_html)
            email.attach_alternative(body_html_template.render(context), 'text/html')

        return email

    def send(self, request=None, from_email=None, to=None, cc=None, bcc=None, reply_to=None, context=None, attachments=None, alternatives=None, fail_silently=True, auth_user=None, auth_password=None, connection=None, headers=None, noreply=False, language=None, subject=None, body=None):
        email = self.create(
            request=request,
            from_email=from_email,
            to=to,
            cc=cc,
            bcc=bcc,
            reply_to=reply_to,
            context=context,
            attachments=attachments,
            alternatives=alternatives,
            auth_user=auth_user,
            auth_password=auth_password,
            connection=connection,
            headers=headers,
            noreply=noreply,
            language=language,
            subject=subject,
            body=body,
        )

        email.send(fail_silently=fail_silently)

        return email


@python_2_unicode_compatible
class EmailTemplateTranslation(models.TranslationModel):
    parent = models.ForeignKey(
        EmailTemplate,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_('parent'),
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('subject'),
    )
    body = models.TextField(
        verbose_name=_('body'),
    )
    body_html = models.TextField(
        blank=True,
        default='',
        verbose_name=_('body'),
    )

    class Meta:
        unique_together = [('language', 'parent')]
        verbose_name = _('mail translation')
        verbose_name_plural = _('mail translations')

    def __str__(self):
        return "%(name)s [%(lang)s]" % {
            'name': self.parent.name,
            'lang': self.language[:2],
        }


@python_2_unicode_compatible
class Email(models.TimestampModel):
    from_email = models.CharField(
        max_length=255,
        default=_get_default_from_email,
        verbose_name=_('from email'),
    )
    to_emails = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('to emails'),
    )
    cc_emails = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('cc emails'),
    )
    bcc_emails = models.CharField(
        max_length=255,
        blank=True,
        default='',
        verbose_name=_('bcc emails'),
    )
    all_recipients = models.TextField(
        blank=True,
        default='',
        verbose_name=_('recipients'),
    )
    headers =  models.TextField(
        blank=True,
        default='',
        verbose_name=_('headers'),
    )
    subject = models.CharField(
        max_length=255,
        verbose_name=_('subject'),
    )
    body = models.TextField(
        verbose_name=_('body'),
    )
    raw = models.TextField(
        blank=True,
        default='',
        verbose_name=_('raw message'),
    )

    class Meta:
        #ordering = ('name',)
        verbose_name = _('email')
        verbose_name_plural = _('emails')

    def __str__(self):
        return _('Email from "%(from_email)s" to "%(to_emails)s" sent at %(sent_at)s about "%(subject)s"') % {
            'from_email': self.from_email,
            'to_emails': self.to_emails,
            'sent_at': self.created_at,
            'subject': self.subject,
        }

    @property
    def attachment_count(self):
        if not hasattr(self, 'attachment_count_cache'):
            self.attachment_count_cache = self.attachments.count()
        return self.attachment_count_cache


class Attachment(models.Model):
    email = models.ForeignKey(
        Email,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('email'),
    )
    filename = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('filename'),
    )
    content = models.BinaryField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_('content'),
    )
    mimetype = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('mimetype'),
    )

    class Meta:
        #ordering = ('name',)
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')
