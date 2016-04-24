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

from __future__ import absolute_import, division, print_function, unicode_literals
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.encoding import force_text
from django.utils.encoding import python_2_unicode_compatible
from fluo.db import models


class LogManager(models.Manager):
    def log(self, level=None, message="", user=None, object=None, realm=None):
        kwargs = {
            "message": message,
        }
        if level is not None:
            kwargs["level"] = level
        if user is not None:
            kwargs["user"] = user
        if object is not None:
            kwargs["content_type_id"] = ContentType.objects.get_for_model(object).pk
            kwargs["object_id"] = object.pk
            kwargs["object_repr"] = force_text(object)[:255]
        if realm is not None:
            kwargs["realm"] = realm

        log = self.model(**kwargs)
        log.save()
        return log

    def debug(self, message, user=None, object=None, realm=None):
        return self.log(level=Log.DEBUG, message=message, user=user, object=object, realm=realm)

    def info(self, message, user=None, object=None, realm=None):
        return self.log(level=Log.INFO, message=message, user=user, object=object, realm=realm)

    def warning(self, message, user=None, object=None, realm=None):
        return self.log(level=Log.WARNING, message=message, user=user, object=object, realm=realm)

    def error(self, message, user=None, object=None, realm=None):
        return self.log(level=Log.ERROR, message=message, user=user, object=object, realm=realm)

    def critical(self, message, user=None, object=None, realm=None):
        return self.log(level=Log.CRITICAL, message=message, user=user, object=object, realm=realm)


@python_2_unicode_compatible
class Log(models.Model):
    NOTSET = "notset"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

    objects = LogManager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        verbose_name=_("user"),
    )
    timestamp = models.CreationDateTimeField(
        null=True,
        blank=True,
        verbose_name=_("timestamp"),
    )
    level = models.CharField(
        max_length=255,
        default=NOTSET,
        choices=(
            (NOTSET, _("Not set")),
            (DEBUG, _("Debug")),
            (INFO, _("Info")),
            (WARNING, _("Warning")),
            (ERROR, _("Error")),
            (CRITICAL, _("Critical")),
        ),
        verbose_name=_("level"),
    )
    content_type = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        verbose_name=_("content type"),
    )
    object_id = models.TextField(
        default="",
        blank=True,
        #null=True,
        verbose_name=_("object id"),
    )
    object_repr = models.CharField(
        max_length=255,
        default="",
        blank=True,
        verbose_name=_("object repr"),
    )
    message = models.TextField(
        default="",
        blank=True,
        verbose_name=_("message"),
    )
    realm = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("realm"),
        help_text=_("realm"),
    )

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = _("log")
        verbose_name_plural = _("logs")

    def __str__(self):
        msg = ugettext("{timestamp} {level} {message}")
        return msg.format(
            timestamp=self.timestamp,
            level=self.level,
            message=self.message[:255],
        )
