"""
sentry_custom_mailer.plugin
~~~~~~~~~~~~~~~~~~~~~~~~~~~

:author: Kieran Broekhoven <kbroekhoven@clearpathrobotics.com>
:copyright: (c) 2016, Clearpath, All rights reserved.
:license: BSD, see LICENSE for details
"""
from __future__ import absolute_import

import logging

from django.conf import settings
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse
from django import forms
from multi_email_field.forms import MultiEmailField, MultiEmailWidget

from sentry.plugins.sentry_mail.models import MailPlugin
from sentry.models import Activity, UserOption, Release
from sentry.utils.http import absolute_uri
from sentry.utils.email import MessageBuilder, group_id_to_email

import sentry_custom_mailer

NOTSET = object()

logger = logging.getLogger(__name__)


class AddEmailForm(forms.Form):
    """
    Configuration form that allows the user to input desired notification
    recipients.
    """
    emails = MultiEmailField(widget=MultiEmailWidget())


class CustomMailerPlugin(MailPlugin):
    """
    Class for a Sentry plugin that allows a user to specify recipients
    of a project's notification emails.
    """
    title = "Custom Mailer"
    conf_key = 'custom-mailer'
    conf_title = "Custom Mailer"
    slug = 'custom-mailer'
    version = sentry_custom_mailer.VERSION

    author = "Kieran Broekhoven"
    author_url = "https://github.com/clearpathrobotics/sentry-custom-mailer"

    project_default_enabled = True
    project_conf_form = AddEmailForm
    subject_prefix = settings.EMAIL_SUBJECT_PREFIX

    def _build_message(self, subject, template=None, html_template=None,
                       body=None, project=None, group=None, headers=None,
                       context=None):
        """
        Identical function to _build_message for sentry_mail, by the Sentry
        Team, except for the send_to list that is received is assigned to
        the message's list instead of appended. 
        """

        send_to = self.get_option('emails', project) or []
        if not send_to:
            logger.debug('Skipping message rendering, no users to send to.')
            return

        subject_prefix = self.get_option('subject_prefix', project) or \
                self.subject_prefix
        subject_prefix = force_text(subject_prefix)
        subject = force_text(subject)

        msg = MessageBuilder(
            subject='%s%s' % (subject_prefix, subject),
            template=template,
            html_template=html_template,
            body=body,
            headers=headers,
            context=context,
            reference=group,
        )
        msg._send_to = set(send_to)

        return msg

    def notify_about_activity(self, activity):
        if activity.type not in \
                (Activity.NOTE, Activity.ASSIGNED, Activity.RELEASE):
            return

        candidate_ids = set(self.get_send_to(activity.project))
        # Never send a notification to the user that performed the action.
        candidate_ids.discard(activity.user_id)

        if activity.type == Activity.ASSIGNED:
            # Only notify the assignee, and only if they are in the candidate set.
            recipient_ids = candidate_ids & \
                    set(map(int, (activity.data['assignee'],)))
        elif activity.type == Activity.NOTE:
            recipient_ids = candidate_ids - set(
                UserOption.objects.filter(
                    user__in=candidate_ids,
                    key='subscribe_notes',
                    value=u'0',
                ).values_list('user', flat=True)
            )
        else:
            recipient_ids = candidate_ids

        if not recipient_ids:
            return

        project = activity.project
        org = project.organization
        group = activity.group

        headers = {}

        context = {
            'data': activity.data,
            'author': activity.user,
            'project': project,
            'project_link': absolute_uri(reverse('sentry-stream', kwargs={
                'organization_slug': org.slug,
                'project_id': project.slug,
            })),
        }

        if group:
            group_link = absolute_uri('/{}/{}/issues/{}/'.format(
                org.slug, project.slug, group.id
            ))
            activity_link = '{}activity/'.format(group_link)

            headers.update({
                'X-Sentry-Reply-To': group_id_to_email(group.id),
            })

            context.update({
                'group': group,
                'link': group_link,
                'activity_link': activity_link,
            })

        # TODO(dcramer): abstract each activity email into its own helper class
        if activity.type == Activity.RELEASE:
            context.update({
                'release': Release.objects.get(
                    version=activity.data['version'],
                    project=project,
                ),
                'release_link': absolute_uri('/{}/{}/releases/{}/'.format(
                    org.slug,
                    project.slug,
                    activity.data['version'],
                )),
            })

        template_name = activity.get_type_display()

        # TODO: Everything below should instead use `_send_mail` for consistency.
        subject_prefix = project.get_option(
                'subject_prefix', settings.EMAIL_SUBJECT_PREFIX)
        if subject_prefix:
            subject_prefix = subject_prefix.rstrip() + ' '

        if group:
            subject = '%s%s' % (subject_prefix, group.get_email_subject())
        elif activity.type == Activity.RELEASE:
            subject = '%sRelease %s' % \
                    (subject_prefix, activity.data['version'])
        else:
            raise NotImplementedError

        msg = MessageBuilder(
            subject=subject,
            context=context,
            template='sentry/emails/activity/{}.txt'.format(template_name),
            html_template='sentry/emails/activity/{}.html'.format(template_name),
            headers=headers,
            reference=activity,
            reply_reference=group,
        )
	recipients = self.get_option('emails', project) or []
        msg._send_to.update(recipients)
        msg.send()

# Legacy compatibility
MailProcessor = CustomMailerPlugin

