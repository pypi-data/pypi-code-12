# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import logging

from django.conf import settings
from django.db import models, IntegrityError
from django_redis import get_redis_connection
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from .settings import INFO_PREFIX, INFO_TIMEOUT, PREFIX
from .session import SessionStore, DataBaseStore
from .constants import (MAX_KEY_LENGTH,
                        MAX_PREFIX_LENGTH,
                        GLOBAL_PREFIX,
                        INFO_KEY,
                        DEFAULT_PREFIX,
                        INFO_EXIST_VALUE,
                        META_IP,
                        META_AGENT,
                        IP_KEY)


logger = logging.getLogger(__name__)


class SessionInfo(models.Model):
    """
    Session-related information
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sessions',
                             db_index=True, verbose_name=_('User'), null=True)
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Creation date'))
    key = models.CharField(max_length=MAX_KEY_LENGTH, db_index=True, verbose_name=_('Key'))
    prefix = models.CharField(max_length=MAX_PREFIX_LENGTH, db_index=True, default=DEFAULT_PREFIX)
    active = models.BooleanField(default=True)

    # additional request data
    user_ip = models.GenericIPAddressField(default='127.0.0.1', db_index=True)
    user_agent = models.TextField(null=True, default=None, blank=True)

    # auto-generated data on .save()
    user_agent_md5 = models.CharField(max_length=32, default=None, null=True, blank=True)

    @classmethod
    def get_key(cls, session_key):
        return ':'.join([INFO_PREFIX, GLOBAL_PREFIX, INFO_KEY, session_key])

    @classmethod
    def _get_ip_key(cls, session_key):
        return ':'.join([INFO_PREFIX, GLOBAL_PREFIX, INFO_KEY, IP_KEY, session_key])

    @classmethod
    def get_ip(cls, session_key):
        key = cls._get_ip_key(session_key)
        conn = get_redis_connection()
        v = conn.get(key)
        if not v:
            s = SessionInfo.get_or_none(session_key)
            if not s:
                logger.warning('unable to find session info for %s' % session_key)
                return None
            v = s.user_ip
            conn.setex(key, INFO_TIMEOUT, v)
        return v

    @classmethod
    def is_request_valid(cls, request):
        session_key = request.session.session_key
        session_ip = cls.get_ip(session_key)
        current_ip = request.META.get(META_IP)
        logger.info('key: %s, session_ip: %s, current: %s' % (session_key, session_ip, current_ip))
        return session_ip == current_ip

    @classmethod
    def key_exists(cls, session_key):
        """
        If session info exists with that session_key, returns True
        """
        key = cls.get_key(session_key)
        conn = get_redis_connection()
        return conn.exists(key)

    @staticmethod
    def exists(request):
        return SessionInfo.key_exists(request.session.session_key)

    @classmethod
    def gen(cls, request):
        """
        Generate Session model from request
        """
        session = SessionInfo(user=request.user, key=request.session.session_key)

        # additional request data processing
        session.user_ip = request.META.get(META_IP)
        session.user_agent = force_text(request.META.get(META_AGENT), errors='replace')

        return session

    @classmethod
    def record(cls, request, prefix=PREFIX):
        """
        Record session info from request
        """
        session_key = request.session.session_key
        logger.info('recording request %s %s' % (session_key, prefix))
        try:
            session = cls.gen(request)
            session.prefix = prefix
            session.save()
        except IntegrityError:
            # session info is already in database
            pass
        conn = get_redis_connection()
        conn.setex(cls.get_key(session_key), INFO_TIMEOUT, INFO_EXIST_VALUE)

    def erase(self):
        self.active = False
        SessionStore(self.key, self.prefix).delete()
        self.save()

    def session_exists(self):
        return SessionStore(self.key, self.prefix).exists()
    session_exists.boolean = True

    def session_exists_db(self):
        return DataBaseStore().exists(self.key)
    session_exists_db.boolean = True

    def session_data(self):
        s = SessionStore(self.key, self.prefix)
        if s.exists(self.key):
            return s.load()
        if self.session_exists_db():
            return DataBaseStore(self.key).load()
        return ugettext('Does not exist')

    def __unicode__(self):
        return '{user}'.format(user=self.user)

    def save(self, *args, **kwargs):
        if self.user_agent:
            self.user_agent_md5 = hashlib.md5(self.user_agent).hexdigest()
        super(SessionInfo, self).save(*args, **kwargs)
        logger.info('saved %s %s session_info' % (self.key, self.prefix))

    @classmethod
    def get_or_none(cls, session_key, prefix=PREFIX):
        try:
            logger.info('getting %s %s session_info' % (session_key, prefix))
            return cls.objects.get(key=session_key, prefix=prefix)
        except cls.DoesNotExist:
            return None

    class Meta:
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')
        unique_together = (('prefix', 'key'),)
