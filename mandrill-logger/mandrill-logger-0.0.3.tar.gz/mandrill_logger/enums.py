# -*- coding: utf-8 -*-
from django.utils.translation import gettext as _
from enumerify.enum import Enum


class LogReason(Enum):
    # The reason for the rejection if the recipient status is
    # "rejected" - one of "hard-bounce", "soft-bounce", "spam", "unsub", "custom", "invalid-sender", "invalid",
    # "test-mode-limit", "unsigned", or "rule"
    NA = 0
    HARD_BOUNCE = 1
    SOFT_BOUNCE = 2
    SPAM = 3
    UNSUB = 4
    CUSTOM = 5
    INVALID_SENDER = 6
    INVALID = 7
    TEST_MODE_LIMIT = 8
    UNSIGNED = 9
    RULE = 10

    i18n = (
        _('Not Available'),
        _('Hard Bounce'),
        _('Soft Bounce'),
        _('Spam'),
        _('Unsub'),
        _('Custom'),
        _('Invalid Sender'),
        _('Invalid'),
        _('Test Mode Limit'),
        _('Unsigned'),
        _('Rule'),
    )


class LogStatus(Enum):
    # The sending status of the recipient - either "sent", "queued", "scheduled", "rejected", or "invalid"
    DEFAULT = 0
    SENT = 1
    QUEUED = 2
    SCHEDULED = 3
    REJECTED = 4
    INVALID = 5

    i18n = (
        _('Default'),
        _('Sent'),
        _('Queued'),
        _('Scheduled'),
        _('Rejected'),
        _('Invalid'),
    )