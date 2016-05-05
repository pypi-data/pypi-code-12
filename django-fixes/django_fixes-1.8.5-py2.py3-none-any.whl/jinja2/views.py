from functools import partial

from django.views.defaults import permission_denied as django_permission_denied
from django.views.defaults import page_not_found as django_page_not_found
from django.views.defaults import server_error as django_server_error

# simply override the template_name for each django view
permission_denied=partial(django_permission_denied,template_name='403.jinja2')
page_not_found=partial(django_page_not_found,template_name='404.jinja2')
server_error=partial(django_server_error,template_name='500.jinja2')
