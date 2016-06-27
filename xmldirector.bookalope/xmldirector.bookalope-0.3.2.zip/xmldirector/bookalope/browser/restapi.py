# -*- coding: utf-8 -*-

################################################################
# xmldirector.bookalope
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################

from zopyx.plone.persistentlogger.logger import IPersistentLogger

from xmldirector.plonecore.browser.restapi import BaseService
from xmldirector.plonecore.browser.restapi import decode_json_payload

from xmldirector.bookalope.browser.api import convert_bookalope


class BookalopeConversionError(Exception):
    """ A generic Bookalope error """


class api_convert_bookalope(BaseService):

    def _render(self):

        IPersistentLogger(self.context).log('bookalope-convert')
        payload = decode_json_payload(self.request)
        if not payload.get('source'):
            raise ValueError('No source file specified')

        print payload
        convert_bookalope(self.context, **payload)
        
