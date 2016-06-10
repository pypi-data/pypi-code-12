# -*- coding: utf-8 -*-
__author__ = 'Thomas'

import gettext

class TranslatedObject:

    def __init__(self,domain):
        self.domain = domain

    def translate(self,domain,localedir, languages):
        print("TRANSLATING the following domain: %s!!!!"%self.domain)
        #i18n = gettext.translation(domain,localedir=localedir,languages=languages)
        #i18n.install()
        pass