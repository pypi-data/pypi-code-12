#!/usr/bin/env python

"""test_nba

Tests for `nba` module.
"""

import unittest

import json
from sportsstats import nba


class TestNba(unittest.TestCase):

    def setUp(self):
        from datetime import datetime
        april_9 = datetime(2016, 4, 9)
        self.nba_stats = nba.Stats(april_9, april_9)
        self.expected_query_url = (
                "/stats/leaguedashptstats?"
                "College=&Conference=&Country=&DateFrom=04%2F09%2F2016&"
                "DateTo=04%2F09%2F2016&Division=&DraftPick=&DraftYear=&"
                "GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&"
                "Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&"
                "PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&"
                "PtMeasureType=SpeedDistance&Season=2015-16&SeasonSegment=&"
                "SeasonType=Regular+Season&StarterBench=&TeamID=0&"
                "VsConference=&VsDivision=&Weight="
        )
        pass

    def tearDown(self):
        del self.nba_stats
        pass

    def test_build_query_url(self):
        actual = self.nba_stats._Stats__build_query_url()
        self.assertEqual(actual, self.expected_query_url)

    def test_send_get_request(self):
        connection = self.nba_stats._Stats__send_get_request(
                self.expected_query_url)
        actual = connection.getresponse().status
        self.assertEqual(actual, 200)
        connection.close()

    def test_download(self):
        data = json.loads(self.nba_stats.download())
        expected = [
            'PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_ABBREVIATION',
            'GP', 'W', 'L', 'MIN', 'DIST_FEET', 'DIST_MILES',
            'DIST_MILES_OFF', 'DIST_MILES_DEF', 'AVG_SPEED',
            'AVG_SPEED_OFF', 'AVG_SPEED_DEF'
        ]
        actual = data['resultSets'][0]['headers']
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
