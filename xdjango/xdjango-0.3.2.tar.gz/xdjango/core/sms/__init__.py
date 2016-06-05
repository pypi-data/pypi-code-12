from xdjango.core.sms.backends.txtlocal import TxtLocalAPI


def send_sms(message, sender, recipient_list, fail_silently=False):
    api = TxtLocalAPI()

    api.sendSms(sender=sender, number=recipient_list[0], message=message)