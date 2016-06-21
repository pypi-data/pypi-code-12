# -*- coding: utf-8 -*-
# :Project:   SoL
# :Created:   lun 16 dic 2013 20:14:45 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2013, 2014, 2016 Lele Gaifax
#

from . import AuthenticatedTestCase


class TestSvgController(AuthenticatedTestCase):

    def test_rating(self):
        from .. import RatingData

        response = self.app.get('/data/ratings')
        result = response.json
        self.assertEqual(result['success'], True)
        self.assertEqual(result['message'], "Ok")
        self.assertEqual(result['root'][0]['description'],
                         RatingData.european.description)

        idrating = result['root'][0]['idrating']
        guidrating = result['root'][0]['guid']

        response = self.app.get('/data/ratedPlayers?filter_idrating=%d' % idrating)
        result = response.json

        idp1 = result['root'][0]['idplayer']
        idp2 = result['root'][1]['idplayer']
        idp3 = result['root'][2]['idplayer']
        idp4 = result['root'][3]['idplayer']
        guidp1 = result['root'][0]['guid']
        guidp2 = result['root'][1]['guid']
        guidp3 = result['root'][2]['guid']
        guidp4 = result['root'][3]['guid']

        response = self.app.get(('/svg/ratingchart/%d?idplayer=' % idrating)
                                + '&idplayer='.join(map(str, [idp1, idp2, idp3, idp4])))
        self.assert_(response.text.startswith(
            '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<svg'))

        response = self.app.get(('/svg/ratingchart/%s?player=' % guidrating)
                                + '&player='.join([guidp1, guidp2, guidp3, guidp4]))
        self.assert_(response.text.startswith(
            '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<svg'))

    def test_players_distribution(self):
        response = self.app.get('/svg/playersdist')
        self.assert_(response.text.startswith(
            '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<svg'))

    def test_opponents(self):
        from sqlalchemy import and_, select
        from ...models import DBSession, Competitor, Match, Player

        s = DBSession()
        mt = Match.__table__
        ct1 = Competitor.__table__.alias('c1')
        ct2 = Competitor.__table__.alias('c2')
        pt1 = Player.__table__.alias('p1')
        pt2 = Player.__table__.alias('p2')
        q = select([pt1.c.guid, pt2.c.guid],
                   and_(ct1.c.idplayer1 == pt1.c.idplayer,
                        ct2.c.idplayer1 == pt2.c.idplayer,
                        mt.c.idcompetitor1 == ct1.c.idcompetitor,
                        mt.c.idcompetitor2 == ct2.c.idcompetitor))
        r = s.execute(q).first()
        response = self.app.get('/svg/player/%s/%s' % (r[0], r[1]))
        self.assert_(response.text.startswith(
            '<?xml version=\'1.0\' encoding=\'utf-8\'?>\n<svg'))
