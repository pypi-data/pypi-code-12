#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'bac'
from kombu.transport import TRANSPORT_ALIASES
# from celery.backends import BACKEND_ALIASES

TRANSPORT_ALIASES["emq"] = __name__ + '.transport:EMQTransport'
# BACKEND_ALIASES["emqcache"] = 'emq_celery.backend:EMQCacheBackend'
