# -*- coding: utf-8 -*-
# :Project:   SoL
# :Created:   sab 10 gen 2015 13:41:58 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2015 Lele Gaifax
#

from . import FunctionalTestCase


class TestStatics(FunctionalTestCase):

    def test_favicon(self):
        self.app.get('/favicon.ico')

    def test_robots(self):
        self.app.get('/robots.txt')
