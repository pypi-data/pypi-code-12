# coding: utf-8
from m3_ext.views import workspace as m3_workspace

__author__ = 'damirazo <me@damirazo.ru>'


def workspace(request):
    return m3_workspace('demo_workspace.html')(request)
