from __future__ import absolute_import
import logging
import os
import random as insecure_random
from django.conf import settings

logger = logging.getLogger("django.randomfields.random")
secure_random = insecure_random.SystemRandom()

try:
    os.urandom(1)
except NotImplementedError:
    urandom_available = False
else:
    urandom_available = True

log_exceptions = urandom_available or "randomfields.models.fields.base.RandomFieldMixin.InsecurePRNG" not in settings.SILENCED_SYSTEM_CHECKS

def randint(*args):
    try:
        return secure_random.randint(*args)
    except NotImplementedError:
        if log_exceptions:
            logger.exception("Encountered 'secure_random.randint' NotImplementedError. Falling back to 'insecure_random.randint'.")
    return insecure_random.randint(*args)

def choice(seq):
    try:
        return secure_random.choice(seq)
    except NotImplementedError:
        if log_exceptions:
            logger.exception("Encountered 'secure_random.choice' NotImplementedError. Falling back to 'insecure_random.choice'.")
    return insecure_random.choice(seq)