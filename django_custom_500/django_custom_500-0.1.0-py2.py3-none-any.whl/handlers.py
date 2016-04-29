# !/usr/bin/python
# coding=utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

from django.conf import settings
from django.http import HttpResponseServerError
from django.template import Context, loader


def handler500(request):
    """
    500 error handler which includes ``request`` in the context.

    Template: `500.html`
    Context: None
    """

    template_500 = getattr(settings, 'CUSTOM_500_TEMPLATE', '500.html')
    template = loader.get_template(template_500)

    return HttpResponseServerError(
        template.render(
            Context(
                {
                    'request': request
                }
            )
        )
    )
