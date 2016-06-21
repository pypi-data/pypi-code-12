# -*- coding: utf-8 -*-
# :Project:   SoL -- Tests for the auth views
# :Created:   sab 11 giu 2016 23:44:52 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from . import FunctionalTestCase


class TestAcceptLanguage(FunctionalTestCase):
    USERNAME = 'Lele'
    PASSWORD = 'lele'

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        response = cls.app.post('/auth/login',
                                {'username': cls.USERNAME, 'password': cls.PASSWORD},
                                headers={'Accept-Language': 'en'})
        assert response.json['reload_l10n']
