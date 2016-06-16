
"""

"""

from tingyun.packages import six
from tingyun.armoury.ammunition.external_tracker import wrap_external_trace


def detect(module):
    def url_opener_open(instance, fullurl, *args, **kwargs):
        """
        :param instance:
        :param fullurl:
        :param args:
        :param kwargs:
        :return:
        """
        if isinstance(fullurl, six.string_types):
            return fullurl
        else:
            return fullurl.get_full_url()

    wrap_external_trace(module, 'OpenerDirector.open', 'urllib2', url_opener_open)
