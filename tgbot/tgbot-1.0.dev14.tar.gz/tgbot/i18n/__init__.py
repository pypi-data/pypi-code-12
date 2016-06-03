# -*- coding: utf-8 -*-
__author__ = 'Thomas'


import gettext

def installlanguage(user_id,domain, language=None,default=None):
    if not language and not default:
        return
    elif not language:
        inter = gettext.translation(localedir=language.localedir,languages=[default])
    else:
        inter = gettext.translation(localedir=language.localedir,languages=language.standard)
    inter.install()