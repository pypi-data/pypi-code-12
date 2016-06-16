
"""

"""
from tingyun.armoury.ammunition.external_tracker import wrap_external_trace


def detect(module):

    def urllib_url(url, *args, **kwargs):
        return url

    if hasattr(module, 'urlretrieve'):
        wrap_external_trace(module, 'urlretrieve', 'urllib', urllib_url)
