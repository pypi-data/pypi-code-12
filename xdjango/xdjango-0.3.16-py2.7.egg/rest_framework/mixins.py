from django.http import Http404


class SecureGetObjectMixin(object):
    """
    Secure get object avoiding information leaks.
    """
    def get_object(self):
        try:
            return super(SecureGetObjectMixin, self).get_object()
        except:
            raise Http404