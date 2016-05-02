"""The command, that fetches the information from the configured servers."""
import os
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta

import requests
from django_libs.utils.email import send_email
from django_libs.decorators import lockfile

from ... import default_settings
from ...models import Server, ServerLog, get_parsed_response
from ...constants import SERVER_STATUS

LOCKFILE = os.path.join(settings.LOCKFILE_FOLDER, 'guardian_fetch')


class Command(BaseCommand):

    def send_error_email(self, serverlog):
        context = {
            'server': serverlog.server,
            'subject': u'{0} {1} - {2}'.format(
                serverlog.status, serverlog.status_code, serverlog.server.name
            ),
            'status': serverlog,
        }
        send_email(
            {},
            context,
            'server_guardian/email/email_subject.html',
            'server_guardian/email/warning_email_body.html',
            settings.FROM_EMAIL,
            [admin[1] for admin in settings.ADMINS],
        )

    def get_email_required(self, serverlog):
        """Send a warning email, if the server response contains errors."""

        # when the status code is included in our setting
        if serverlog.status_code in default_settings.EMAIL_ON_STATUS:
            return True

        try:
            # when the server transitions to a status of DANGER
            if serverlog.status == SERVER_STATUS['DANGER'] and (
                serverlog.get_previous().status != SERVER_STATUS['DANGER']
            ):
                return True

            # when the server transitions to a status that is not DANGER
            if serverlog.status != SERVER_STATUS['DANGER'] and (
                serverlog.get_previous().status == SERVER_STATUS['DANGER']
            ):
                return True
        except (KeyError, TypeError) as ex:
            serverlog.content = (
                'Server got an error "{0}" and returned the following content:'
                '{1}'.format(ex, serverlog.content)
            )
            serverlog.save()
            return True

        return False

    @lockfile(LOCKFILE)
    def handle(self, *args, **options):
        count = 0
        mails_sent = 0

        for server in Server.objects.all():
            response = requests.get(url=server.url, params={
                'token': server.token
            })
            server.last_updated = now()
            server.save()
            parsed_response = get_parsed_response(response.content)
            for status in parsed_response:
                if type(status) == dict:
                    serverlog = ServerLog.objects.create(
                        server=server,
                        content=status['info'],
                        status=status['status'],
                        label=status.get('label', 'no label'),
                        status_code=response.status_code,
                    )
                    if self.get_email_required(serverlog):
                        self.send_error_email(serverlog)
                        mails_sent += 1
                else:
                    self.send_error_email(serverlog)
                    mails_sent += 1
            if server.log_age:
                ServerLog.objects.filter(
                    time_logged__lt=now() - timedelta(days=server.log_age)
                ).delete()
            count += 1

        sys.stdout.write(
            '[{0}] Updated {1} servers. Sent {2} warning emails.\n'.format(
                now(), count, mails_sent)
        )
