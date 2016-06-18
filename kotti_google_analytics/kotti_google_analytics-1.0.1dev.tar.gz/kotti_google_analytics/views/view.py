# -*- coding: utf-8 -*-

"""
Created on 2016-06-18
:author: Oshane Bailey (b4.oshany@gmail.com)
"""

from pyramid.view import view_config
from pyramid.view import view_defaults

from kotti_google_analytics import _, AnayticsDefault
from kotti_google_analytics.fanstatic import css_and_js
from kotti_google_analytics.views import BaseView


@view_config(
    name='analytics-code',
    renderer='kotti_google_analytics:templates/tracking_code.pt')
class CartView(BaseView):

    def __call__(self):
        print AnayticsDefault.tracking_id
        return {
            "tracking_id": AnayticsDefault.tracking_id
        }