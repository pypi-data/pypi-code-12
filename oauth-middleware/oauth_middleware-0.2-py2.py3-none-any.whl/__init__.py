from __future__ import division, unicode_literals, print_function, absolute_import

__version__ = __VERSION__ = "0.2"


from .middleware import make_oauth_wsgi
from .providers.zalando import make_zalando_oauth
