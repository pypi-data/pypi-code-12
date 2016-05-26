#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'bac'
from kombu.transport import TRANSPORT_ALIASES

# from celery.backends import BACKEND_ALIASES

TRANSPORT_ALIASES["emq"] = __name__ + '.transport:EMQTransport'


# BACKEND_ALIASES["emqcache"] = 'emq_celery.backend:EMQCacheBackend'

def _format_queue_name(name):
    """
    格式化celery的quque名称，因为emq对名称有格式限制
    :param name:
    :return:
    """
    name, number = re.subn('[^a-zA-Z0-9_]', '_', name)
    return name
