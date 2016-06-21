# -*- coding: utf-8 -*-
# :Project:   SoL
# :Created:   ven 31 ott 2008 16:56:00 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008, 2010, 2013, 2014, 2016 Lele Gaifax
#

from datetime import datetime

from webtest.app import AppError

from . import FunctionalTestCase

import transaction


class TestPdf(FunctionalTestCase):
    def setUp(self):
        from ...models import DBSession, Tourney
        from .. import TourneyData

        super().setUp()

        with transaction.manager:
            s = DBSession()

            tourney = s.query(Tourney).filter_by(description=TourneyData.rated.description).one()

            if not tourney.prized:
                tourney.makeFinalTurn()
                finals = [m for m in tourney.matches if m.final]
                finals[0].score2 = 10

                tourney.makeNextTurn()
                finals = [m for m in tourney.matches if m.final]
                finals[1].score1 = 10

                tourney.makeNextTurn()
                finals = [m for m in tourney.matches if m.final]
                finals[2].score2 = 20

                tourney.updateRanking()

            self.tourney_id = tourney.idtourney
            self.tourney_guid = tourney.guid
            self.rating_id = tourney.rating.idrating
            self.rating_guid = tourney.rating.guid
            self.cship_id = tourney.championship.idchampionship
            self.cship_guid = tourney.championship.guid

    def test_participants(self):
        self.app.get('/pdf/participants/%s' % self.tourney_id)
        self.app.get('/pdf/participants/%s' % self.tourney_guid)

    def test_ranking(self):
        from ...models import DBSession, Tourney
        from .. import TourneyData

        self.app.get('/pdf/ranking/%s' % self.tourney_id)
        self.app.get('/pdf/ranking/%s' % self.tourney_guid)

        s = DBSession()

        with transaction.manager:
            tourney = s.query(Tourney).filter_by(description=TourneyData.asis.description).one()
            if not tourney.prized:
                tourney.updateRanking()
                tourney.assignPrizes()
            tourney_id = tourney.idtourney

        self.app.get('/pdf/ranking/%s' % tourney_id)

        s = DBSession()

        tourney = s.query(Tourney).filter_by(description=TourneyData.apr24.description).one()

        self.app.get('/pdf/ranking/%s' % tourney.idtourney)
        self.app.get('/pdf/ranking/%s?turn=1' % tourney.idtourney)
        self.assertRaises(AppError, self.app.get,
                          '/pdf/ranking/%s?turn=foo' % tourney.idtourney)

    def test_nationalranking(self):
        from ...models import DBSession, Tourney
        from .. import TourneyData

        self.app.get('/pdf/nationalranking/%s' % self.tourney_id)
        self.app.get('/pdf/nationalranking/%s' % self.tourney_guid)

        s = DBSession()

        tourney = s.query(Tourney).filter_by(description=TourneyData.first.description).one()

        self.app.get('/pdf/nationalranking/%s' % tourney.idtourney)

    def test_results(self):
        self.app.get('/pdf/results/%s' % self.tourney_id)
        self.app.get('/pdf/results/%s' % self.tourney_guid)

    def test_all_results(self):
        self.app.get('/pdf/results/%s?turn=0' % self.tourney_id)
        self.app.get('/pdf/results/%s?turn=0' % self.tourney_guid)
        self.app.get('/pdf/results/%s?turn=all' % self.tourney_id)
        self.app.get('/pdf/results/%s?turn=all' % self.tourney_guid)

    def test_matches(self):
        self.app.get('/pdf/matches/%s' % self.tourney_id)
        self.app.get('/pdf/matches/%s' % self.tourney_guid)

    def test_scorecards(self):
        self.app.get('/pdf/scorecards/%s' % self.tourney_id)
        self.app.get('/pdf/scorecards/%s' % self.tourney_guid)
        self.app.get('/pdf/scorecards/%s?starttime=%f'
                     % (self.tourney_guid, datetime.now().timestamp()))
        self.app.get('/pdf/scorecards/%s?starttime=%d'
                     % (self.tourney_guid, datetime.now().timestamp() * 1000))
        self.assertRaises(AppError, self.app.get,
                          '/pdf/scorecards/%s?starttime=foo' % self.tourney_guid)

    def test_badges(self):
        from ...models import DBSession, Tourney
        from .. import TourneyData

        self.app.get('/pdf/badges/%s' % self.tourney_id)
        self.app.get('/pdf/badges/%s' % self.tourney_guid)

        s = DBSession()

        with transaction.manager:
            tourney = s.query(Tourney).filter_by(description=TourneyData.asis.description).one()
            if not tourney.prized:
                tourney.updateRanking()
                tourney.assignPrizes()
            tourney_id = tourney.idtourney

        self.app.get('/pdf/badges/%s' % tourney_id)

    def test_championshipranking(self):
        self.app.get('/pdf/championshipranking/%s' % self.cship_id)
        self.app.get('/pdf/championshipranking/%s' % self.cship_guid)

    def test_ratingranking(self):
        self.app.get('/pdf/ratingranking/%s' % self.rating_id)
        self.app.get('/pdf/ratingranking/%s' % self.rating_guid)
