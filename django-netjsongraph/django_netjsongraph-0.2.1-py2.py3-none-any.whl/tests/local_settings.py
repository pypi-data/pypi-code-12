# RENAME THIS FILE TO local_settings.py IF YOU NEED TO CUSTOMIZE SOME SETTINGS
# BUT DO NOT COMMIT

from django.conf import settings

settings.INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar'
]

INTERNAL_IPS = ['10.40.0.56', '10.40.0.55', '193.205.218.194']

import sys
if 'test' not in sys.argv:
    #NETJSONGRAPH_SIGNALS = 'ninux_whois'
    pass
