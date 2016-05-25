"""
WSGI config for ip registry (iprir) project

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

"""
# WSGIPythonPath ~/iprir

<VirtualHost *:80>

    ...

    WSGIScriptAlias /ip /var/www/wsgi/iprir.wsgi

    <Directory /var/www/wsgi>
    Order allow,deny
    Allow from all
    </Directory>

"""

import os
import sys

sys.path.append('~/iprir')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iprir.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
