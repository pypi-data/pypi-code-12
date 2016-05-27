from django.conf import settings
import datetime

SMS_ENABLED = getattr(settings, 'REGISTRATIONS_SMS_ENABLED', False)
TWILIO_ACCOUNT = getattr(settings, 'REGISTRATIONS_TWILIO_ACCOUNT', None)
TWILIO_TOKEN = getattr(settings, 'REGISTRATIONS_TWILIO_TOKEN', None)
TWILIO_OUTBOUND_NUMBER = getattr(settings, 'REGISTRATIONS_TWILIO_OUTBOUND_NUMBER', None)

EMAIL_VERIFICATION_TIMEDELTA = getattr(settings, 'REGISTRATIONS_EMAIL_VERIFICATION_TIMEDELTA',
                                       datetime.timedelta(days=7))
SMS_VERIFICATION_TIMEDELTA = getattr(settings, 'REGISTRATIONS_EMAIL_VERIFICATION_TIMEDELTA',
                                     datetime.timedelta(minutes=30))
