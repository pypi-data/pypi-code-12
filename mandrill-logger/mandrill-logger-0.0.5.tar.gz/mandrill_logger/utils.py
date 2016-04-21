from django.contrib.auth import get_user_model

from .enums import LogReason, LogStatus
from .models import Log


class MandrillLogger():
    REASON_TRANSLATOR = {
        'hard-bounce': LogReason.HARD_BOUNCE,
        'soft-bounce': LogReason.SOFT_BOUNCE,
        'spam': LogReason.SPAM,
        'unsub': LogReason.UNSUB,
        'custom': LogReason.CUSTOM,
        'invalid-sender': LogReason.INVALID_SENDER,
        'invalid': LogReason.INVALID,
        'test-mode-limit': LogReason.TEST_MODE_LIMIT,
        'unsigned': LogReason.UNSIGNED,
        'rule': LogReason.RULE,
    }
    # The sending status of the recipient - either "sent", "queued", "scheduled", "rejected", or "invalid"
    STATUS_TRANSLATOR = {
        'sent': LogStatus.SENT,
        'queued': LogStatus.QUEUED,
        'scheduled': LogStatus.SCHEDULED,
        'rejected': LogStatus.REJECTED,
        'invalid': LogStatus.INVALID,
    }

    def __init__(self):
        pass

    def log_email(self, email):
        mandrill_response = email.mandrill_response[0]
        _data = {}
        _data['email'] = mandrill_response['email']
        _data['user'] = self.get_user_from_email(mandrill_response['email'])
        _data['mandrill_id'] = mandrill_response['_id']
        _data['meta_data'] = mandrill_response
        _data['status'] = self.get_status_enum(mandrill_response.get('status', None))
        _data['reason'] = self.get_reason_enum(mandrill_response.get('reject_reason', None))
        _data['template'] = email.template_name
        self.save_log(_data)

    def save_log(self, _data):
        Log.objects.create(**_data)

    def get_user_from_email(self, email):
        user = get_user_model()
        try:
            return user.objects.get(email=email)
        except Exception as e:
            print e
            return None

    def get_reason_enum(self, reason):
        return self.translate_enum(self.REASON_TRANSLATOR, reason, LogReason.NA)

    def get_status_enum(self, status):
        return self.translate_enum(self.STATUS_TRANSLATOR, status, LogStatus.DEFAULT)

    def translate_enum(self, _dict, _str, _default=None):
        try:
            return _dict[_str]
        except Exception as e:
            return _default
