# -*- coding: utf-8 -*-
from django.utils import timezone
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _
from unidecode import unidecode
import logging
import os
import sys

class BaseJob(object):
    name = u"" # eg. clear_objects
    description = u"" # eg. Removing objects of class A and B older than 30 days

    def __init__(self):
        self.name = self.__module__.split('.')[-1]
#        self.description = u"%s job done" % self.name

    def __str__(self):
        return self.name

    def _run(self, *args, **kwargs):
        raise NotImplementedError("The _run() method should take the one user argument (User), perform a task and return result (dict or SortedDict).")

    def run(self, user, *args, **kwargs):
        logger = logging.getLogger('system.cron.%s' % self.name)

        exc_info = None
        extra = {
            'user': user,
            'extra_info': SortedDict()
        }

        success = None

        start_time = timezone.now()
        try:
            result = self._run(user, *args, **kwargs)
            level = result.pop('level') if 'level' in result else logging.INFO
            message = result.pop('message') if 'message' in result else _("Job completed")
            extra['extra_info'].update(result)
            success = True
        except Exception, e:
            level = logging.ERROR
            message = u"[%s] %s" % (e.__class__.__name__, e)
            exc_info = sys.exc_info()
            success = False
        end_time = timezone.now()
        extra['extra_info']['time'] = end_time - start_time

        logger.log(level, message, exc_info = exc_info, extra = extra)

        return success
