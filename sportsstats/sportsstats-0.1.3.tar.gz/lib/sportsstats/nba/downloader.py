#!/usr/bin/env python

"""nba

Download NBA statistics from: http://stats.nba.com/tracking/
"""

from collections import OrderedDict
from contextlib import closing
import sportsstats.utils

try:
    # Python 3.0+
    from urllib.parse import urlencode
    import http.client as httplib  # works with Python 2 with `future` module
except ImportError:
    # Python 2
    import httplib
    from urllib import urlencode


class DownloadError(Exception):
    pass


class HttpDownloader:
    """NBA Statistics.

    Attributes:
       start (datetime): The start date for the statistics to download.
       end (datetime): The end date for the statistics to download.
    """

    def __init__(self, start, end):
        from datetime import datetime
        # TODO bulletproof this...
        assert isinstance(start, datetime)
        self.start = start
        assert isinstance(end, datetime)
        self.end = end
        self.season = self.__determine_season()

    def download(self):
        """Download NBA statistics.

        Returns:
            The requested statistics as JSON bytes.
        """
        query_url = self.__build_query_url()
        try:
            with closing(self.__send_get_request(query_url)) as connection:
                return connection.getresponse().read().decode('utf-8')
        except httplib.HTTPException as e:
            raise DownloadError(e)

    def __determine_season(self):
        """Attempt to determine the season from `start` and `end`. Note: all we
        care about is the years.

        Returns:
            {'start': datetime, 'end': datetime}: Any date in the starting year
                of the season followed by `self.end`
        """
        if self.start.year == self.end.year:
            start = sportsstats.utils.add_years(self.start, -1)
        else:
            start = self.start
        return {'start': start, 'end': self.end}

    def __send_get_request(self, query_url):
        """Send a get request.

        Returns:
            An HTTPConnection.
        """
        connection = httplib.HTTPConnection('stats.nba.com')
        connection.request('GET', query_url)
        return connection

    def __build_query_url(self):
        """Format the query URl from parameters and a prefix.

        Returns:
            The encoded URL.
        """
        url_prefix = '/stats/leaguedashptstats?'
        start = self.start.strftime("%m/%d/%Y")
        end = self.end.strftime("%m/%d/%Y")
        season = "{}-{}".format(self.season['start'].strftime("%Y"),
                                self.season['end'].strftime("%y"))
        params = OrderedDict([
            ('College', ''),
            ('Conference', ''),
            ('Country', ''),
            ('DateFrom', start),
            ('DateTo', end),
            ('Division', ''),
            ('DraftPick', ''),
            ('DraftYear', ''),
            ('GameScope', ''),
            ('Height', ''),
            ('LastNGames', '0'),
            ('LeagueID', '00'),
            ('Location', ''),
            ('Month', '0'),
            ('OpponentTeamID', '0'),
            ('Outcome', ''),
            ('PORound', '0'),
            ('PerMode', 'Totals'),
            ('PlayerExperience', ''),
            ('PlayerOrTeam', 'Player'),
            ('PlayerPosition', ''),
            ('PtMeasureType', 'SpeedDistance'),
            ('Season', season),
            ('SeasonSegment', ''),
            ('SeasonType', 'Regular Season'),
            ('StarterBench', ''),
            ('TeamID', '0'),
            ('VsConference', ''),
            ('VsDivision', ''),
            ('Weight', '')
        ])
        return url_prefix + urlencode(params)
