#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings


DEFAULTS = {
    'skin': 'skin-blue',
}

ASSETS = {
    'bootstrap_css': '',
    'bootstrap_js': '',

    'jquery': '',

    'font_awesome': '',

    # Charts
    'Chart.js': '',
    'flot': '',
    'morrisjs': '',
    'sparkline': '',

    # Form Elements
    'seiyria-bootstrap-slider': '',
    'ionrangeslider': '',
    '': '', # bootstrap-datepicker
    'bootstrap-daterangepicker': '',
    '': '',
}


def bootstrap_css():
    pass

def bootstrap_js():
    pass