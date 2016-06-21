# -*- coding: utf-8 -*-
# :Project:   SoL
# :Created:   sab 13 dic 2008 16:35:46 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2008, 2010, 2013, 2014, 2015, 2016 Lele Gaifax
#

from . import FunctionalTestCase


class TestLitViews(FunctionalTestCase):

    def test_index(self):
        self.app.get('/lit')

    def test_latest(self):
        from webtest.app import AppError

        self.app.get('/lit/latest')
        self.app.get('/lit/latest?n=10')
        try:
            self.app.get('/lit/latest?n=x')
        except AppError as e:
            self.assertIn('400 Bad Request', str(e))
        else:
            assert False, "Should raise a 400 status"

    def test_championship(self):
        from ...models import DBSession, Championship

        s = DBSession()
        cship = s.query(Championship).first()
        self.app.get('/lit/championship/%s' % cship.guid)

    def test_tourney(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/lit/tourney/%s' % tourney.guid)

    def test_tourney_turn(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        self.app.get('/lit/tourney/%s?turn=1' % tourney.guid)

    def test_tourney_player(self):
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        player = tourney.competitors[0].player1
        self.app.get('/lit/tourney/%s?player=%s' % (tourney.guid, player.guid))

    def test_tourney_player_turn(self):
        from webtest.app import AppError
        from ...models import DBSession, Tourney

        s = DBSession()
        tourney = s.query(Tourney).first()
        player = tourney.competitors[0].player1
        self.app.get('/lit/tourney/%s?player=%s&turn=1' % (tourney.guid, player.guid))
        try:
            self.app.get('/lit/tourney/%s?player=%s&turn=x' % (tourney.guid, player.guid))
        except AppError as e:
            self.assertIn('400 Bad Request', str(e))
        else:
            assert False, "Should raise a 400 status"

    def test_player(self):
        from ...models import DBSession, Player

        s = DBSession()
        player = s.query(Player).first()
        self.app.get('/lit/player/%s' % player.guid)

    def test_merged_player(self):
        from ..data import MergedPlayerData

        self.app.get('/lit/player/%s' % MergedPlayerData.fatta.guid)

    def test_players(self):
        self.app.get('/lit/players')

    def test_players_listing(self):
        from ...models import DBSession, Player

        s = DBSession()
        player = s.query(Player).first()
        self.app.get('/lit/players/%s/%s' % (player.lastname[0], player.nationality))

    def test_rating(self):
        from ...models import DBSession, Rating

        s = DBSession()
        rating = s.query(Rating).first()
        self.app.get('/lit/rating/%s' % rating.guid)

    def test_club(self):
        from ...models import DBSession, Club

        s = DBSession()
        club = s.query(Club).first()
        self.app.get('/lit/club/%s' % club.guid)

    def test_club_players(self):
        from ...models import DBSession, Club

        s = DBSession()
        club = s.query(Club).first()
        self.app.get('/lit/club/%s/players' % club.guid)

    def test_no_club(self):
        from webtest.app import AppError

        try:
            self.app.get('/lit/club/foo')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

    def test_emblem(self):
        from webtest.app import AppError

        response = self.app.get('/lit/emblem/emblem.png')
        assert response.headers['content-type'].startswith('image')

        try:
            self.app.get('/lit/emblem')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

        try:
            self.app.get('/lit/emblem/foo')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

    def test_portrait(self):
        from webtest.app import AppError

        response = self.app.get('/lit/portrait/portrait.png')
        assert response.headers['content-type'].startswith('image')

        try:
            self.app.get('/lit/portrait'),
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

        try:
            self.app.get('/lit/portrait/foo')
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"

    def test_opponent(self):
        from webtest.app import AppError
        from sqlalchemy import and_, select
        from ...models import DBSession, Competitor, Match, Player
        from ..data import MergedPlayerData

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
        self.app.get('/lit/player/%s/%s' % (r[0], r[1]))
        try:
            self.app.get('/lit/player/%s/badc0de' % r[0])
        except AppError as e:
            self.assertIn('404 Not Found', str(e))
        else:
            assert False, "Should raise a 404 status"
        self.app.get('/lit/player/%s/%s' % (r[0], MergedPlayerData.fatta.guid))
        self.app.get('/lit/player/%s/%s' % (MergedPlayerData.fatta.guid, r[0]))
