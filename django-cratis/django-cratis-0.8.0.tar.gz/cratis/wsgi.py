from django.core.wsgi import get_wsgi_application
from cratis.cli import load_env

load_env()

application = get_wsgi_application()
