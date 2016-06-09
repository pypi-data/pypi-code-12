# -*- coding: utf-8 -*-
from plone import api


def register_vendor_js(context):
    """Check if vendor JS are already registered,
       if not register it
    """
    JS_TO_REGISTER = [
        'jquery.cycle2.js',
        'jquery.cycle2.carousel.js',
        'jquery.jplayer.min.js'
    ]

    js_tool = api.portal.get_tool('portal_javascripts')
    for js in JS_TO_REGISTER:
        find_js = False
        for id in js_tool.getResourceIds():
            find_js = (js in id)
            if find_js:
                break
        if not find_js:
            js_tool.registerResource(
                '++resource++brasil.gov.portlets/js/{0}'
                .format(js))
            js_tool.moveResourceBefore(
                '++resource++brasil.gov.portlets/js/{0}'
                .format(js),
                '++resource++brasil.gov.portlets/js/main.js')
    js_tool.cookResources()


def setup_site(context):
    """ Ajustamos o site para receber o produto de agenda
    """
    # Executado apenas se o estivermos no Profile correto
    if context.readDataFile('brasil.gov.portlets.txt') is None:
        return
    site = api.portal.get()
    register_vendor_js(site)
