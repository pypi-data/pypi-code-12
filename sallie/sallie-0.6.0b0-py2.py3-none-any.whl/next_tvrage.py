#pylint: skip-file
# -*- coding: UTF-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__author__ = "d01"
__email__ = "jungflor@gmail.com"
__copyright__ = "Copyright (C) 2016, Florian JUNG"
__license__ = "MIT"
__version__ = "0.1.0"
__date__ = "2016-04-29"
# Created: 2016-04-29 19:20

import pytz
import tvrage.quickinfo

from .tv_next import TVNext

# TODO: add '-e git+https://github.com/the01/python-tvrage.git#egg=tvrage' to the requirements file

# TODO: Migrate to TVNext
class TVNextTVRage(TVNext):
    """
    Check tv shows with tvrage
    """

    def __init__(self, settings=None):
        """
        Initialize object

        :param settings: Settings for instance (default: None)
        :type settings: dict | None
        :rtype: None
        :raises IOError: Could not find 'shows_cache_path'/'shows_path'
        """
        if settings is None:
            settings = {}
        super(TVNextTVRage, self).__init__(settings)

        self._shows = settings.get('shows', {})
        self._showPath = settings.get('shows_cache_path', None)
        self._showNamePath = settings.get('shows_path', None)
        self._tzOrig = settings.get('tvrage_timezone', "US/Pacific")

        if isinstance(self._tzOrig, basestring):
            self._tzOrig = pytz.timezone(self._tzOrig)

        self._accessInterval = settings.get('tvrage_update_interval', 1)
        """ refresh data from tvrage every x days for active shows (default: 1)
            :type _accessInterval: int """
        self._accessHiatusInterval = settings.get(
            'tvrage_update_hiatus_interval', None
        )
        """ refresh interval for shows marked as hiatus (default: None)
        :type _accessHiatusInterval: None | int """
        # refresh interval for show
        self._accessInactiveInterval = settings.get(
            'tvrage_update_inactive_interval', None
        )
        """ refresh interval for shows marked as inactive (default: None)
        :type _accessInactiveInterval: None | int """
        self._requestsPerMinute = settings.get(
            'tvrage_update_requests_per_minute', 0
        )
        """ request per minute using the api - 0 means unlimited (default: 0)
            :type _requestsPerMinute: int """
        self._requests = []
        self._errorSleepTime = settings.get('tvrage_update_retry_delay', 2.0)
        self._maxRetries = settings.get('tvrage_update_retry_num', 3)
        self._shouldRetry = settings.get('tvrage_update_retry', True)

        if self._showPath:
            self._showPath = self.joinPathPrefix(self._showPath)

            if os.path.exists(self._showPath):
                shows = self._loadJSONFile(self._showPath)
                shows.update(self._shows)
                self._shows.update(shows)
            # dont care whether cache file exitsts -> generate it
            # else:
            #    raise IOError(u"File '{}' not found".format(self._showPath))
        if self._showNamePath:
            self._showNamePath = self.joinPathPrefix(self._showNamePath)

            if os.path.exists(self._showNamePath):
                showNames = self._loadJSONFile(self._showNamePath)

                for name in showNames:
                    if name not in self._shows:
                        self._shows[name] = {}
            else:
                raise IOError(u"File '{}' not found".format(self._showNamePath))
            self.debug(u"Loaded show names from {}".format(self._showNamePath))

    @property
    def shows(self):
        """
        Show information

        :return: Shows watching
        :rtype: dict
        """
        return self._shows

    def episodeInfo(self, showname):
        self.debug(u"updating {}".format(showname))

        if self._requestsPerMinute:
            # limit to one minute window
            self._requests = [
                t
                for t in self._requests
                if datetime.datetime.utcnow() - t <= timedelta(minutes=1)
            ]

            if len(self._requests) > self._requestsPerMinute:
                # too many requests -> sleep for a bit
                sleepTime = 60 - (
                    datetime.datetime.utcnow() - self._requests[0]
                ).total_seconds()

                self.warning(u"Too many requests (Sleep {})".format(sleepTime))
                if sleepTime > 0:
                    time.sleep(sleepTime)

        show = tvrage.quickinfo.fetch(showname)

        if "Premiered" in show:
            year = re.findall(r"\s+(\(\d{4}\)|\d{4})$", showname)

            if len(year) > 0:
                year = year[0].strip(" ()")

            if year:
                if show["Premiered"] != year:
                    show2 = tvrage.quickinfo.fetch(
                        re.sub(r"\s+(\(\d{4}\)|\d{4})$", "", showname)
                    )
                    if "Premiered" in show2 and show2["Premiered"] == year:
                        #self.debug("episodeInfo: switch based on year")
                        show = show2

        res = {'latest': None, 'next': None}
        lat = show.get('Latest Episode', None)
        nxt = show.get('Next Episode', None)

        # defaults to 11 pm
        airtime = datetime.time(23, 0)
        if "Airtime" in show:
            air = show['Airtime']
            airsplit = air.split(" at ")

            if len(airsplit) != 2:
                self.warning(u"Unknown airtime format {}".format(air))
            else:
                try:
                    tm = dateutil.parser.parse(airsplit[-1]).time()
                except:
                    self.warning(u"Unknown airtime format {}".format(air))
                else:
                    airtime = tm

        if lat is not None:
            dt = datetime.datetime.combine(
                datetime.datetime.strptime(lat[2], "%b/%d/%Y").date(),
                airtime
            )
            dt = self._tzOrig.localize(dt)
            dt = dt.astimezone(pytz.utc)
            # got it to utc now -> remove timezone
            dt = dt.replace(tzinfo=None)

            res['latest'] = {
                'episode': lat[0],
                'name': lat[1],
                'date': dt
            }

        if nxt is not None:
            try:
                dt = datetime.datetime.strptime(nxt[2], "%b/%d/%Y")
            except:
                try:
                    dt = datetime.datetime.strptime(nxt[2], "%b/%Y")
                except:
                    dt = datetime.datetime.strptime(nxt[2], "%Y")

            dt = datetime.datetime.combine(dt.date(), airtime)
            dt = self._tzOrig.localize(dt)
            dt = dt.astimezone(pytz.utc)
            # got it to utc now -> remove timezone
            dt = dt.replace(tzinfo=None)

            res['next'] = {
                'episode': nxt[0],
                'name': nxt[1],
                'date': dt
            }

        if "Ended" in show and show['Ended']:
            try:
                ended = dateutil.parser.parse(show['Ended'])
            except:
                self.warning(u"Unknown endtime format {}".format(show['Ended']))
            else:
                res['ended'] = ended
        res['status'] = show['Status']
        return res

    def shouldUpdateShow(self, key):
        """
        Decide if show needs updating

        :param key: show key
        :type key: str
        :return: should show be updated
        :rtype: bool
        """
        show = self._shows[key]
        now = datetime.datetime.utcnow()

        # set defaults
        show.setdefault('active', True)
        show.setdefault('hiatus', False)
        accessed = show.get('accessed', None)
        lat = show.get('latest', None)
        nxt = show.get('next', None)
        diff = None

        if accessed:
            diff = now - accessed

        if lat:
            if accessed < lat['date'] < now:
                # last checked before new episode and latest already happened
                # (just to be safe)
                return True
        if nxt and nxt['date'] < now:
                # next already happened
                return True
        if not show['active']:
            if diff is not None and self._accessInactiveInterval:
                # self.debug("Inactive {} ago {}".format(diff, key))
                return diff.days >= self._accessInactiveInterval
            # self.debug("{} inactive".format(key))
            return False
        if show['hiatus']:
            if diff is not None and self._accessHiatusInterval:
                # self.debug("Hiatus {} ago {}".format(diff, key))
                return diff.days >= self._accessHiatusInterval
            # self.debug("{} hiatus".format(key))
            return False

        if diff is None:
            # self.debug("{} not accessed".format(key))
            return True

        # self.debug("Last access {} ago {}".format(diff, key))
        return diff.days >= self._accessInterval

    def updateShow(self, key, autosave=False):
        show = self._shows[key]
        now = datetime.datetime.utcnow()
        latest = show.get('latest', {})

        try:
            info = self.episodeInfo(key)

            if info.get('ended'):
                show['ended'] = info['ended']
            if not info['next']:
                if info['status'] not in ["Returning Series", "New Series"] \
                        and show.get('ended'):
                    show['active'] = False
                    show['hiatus'] = False
                else:
                    show['status'] = True
                    show['hiatus'] = True
                # currently no next show
                show['next'] = None
            else:
                self.debug(u"Next episode on {} ({})".format(
                    info['next']['date'],
                    info['next']['date'] - now
                ))
                show['active'] = True

                if self._accessHiatusInterval:
                    diff = info['next']['date'] - now
                    # next episode far in future -> hiatus
                    show['hiatus'] = diff.days <= self._accessHiatusInterval
                else:
                    # not really the way to leave hiatus
                    # but for now no other possible way..
                    show['hiatus'] = False
                show['next'] = info['next']

            if info['latest']:
                # self.debug("{} got latest".format(key))
                latest = info['latest']
            else:
                self.debug(u"{} -".format(key))
        except Exception as e:
            if "connection reset by peer" not in str(e).lower():
                self.exception("Error updating show")
            raise e

        show['accessed'] = now
        show['errors'] = 0
        show['latest'] = latest
        if self._showPath and autosave:
            try:
                self._saveJSONFile(
                    self._showPath,
                    self._shows,
                    pretty=True,
                    sort=True
                )
            except:
                self.exception("Error saving shows")

    def updateShows(self, forceCheck=False, autosave=False):
        """
        Update all show information

        :param forceCheck: Force reload (default: False)
        :type forceCheck: bool
        :param autosave: Save after each update (default: False)
        :type autosave: bool
        :rtype: None
        """
        for show in sorted(self._shows):
            if not (forceCheck or self.shouldUpdateShow(show)):
                continue
            retry = True
            error_sleep = self._errorSleepTime

            while retry \
                    and self._shows[show].get('errors', 0) < self._maxRetries:
                retry = False

                try:
                    self.updateShow(show, autosave)
                except Exception as e:
                    if "connection reset by peer" in str(e).lower():
                        # Connection reset by peer -> exponential backoff
                        self.warning(
                            u"Connection reset by peer (Sleeping {})".format(
                                error_sleep
                            )
                        )
                        time.sleep(error_sleep)
                        error_sleep *= 2.0
                    else:
                        self.exception(u"Failed to load {}".format(show))
                    self._shows[show]['errors'] = self._shows[show].get(
                        'errors', 0
                    ) + 1
                    retry = self._shouldRetry

    def _compDeltaIn(self, value, minDelta, maxDelta):
        if minDelta > maxDelta:
            temp = minDelta
            minDelta = maxDelta
            maxDelta = temp

        return minDelta <= value <= maxDelta

    def _compDeltaInZero(self, value, delta):
        return self._compDeltaIn(value, timedelta(), delta)

    def check(
            self, forceCheck=False, minDelta=None, maxDelta=None, autosave=False
    ):
        results = []
        if minDelta is None:
            minDelta = timedelta()
        if maxDelta is None:
            maxDelta = timedelta()

        self._requests = []
        self.updateShows(forceCheck, autosave)
        now = datetime.datetime.utcnow().date()
        minDelta = now - minDelta
        maxDelta = now + maxDelta

        for key in sorted(self._shows):
            show = self._shows[key]
            lat = show.get('latest', None)
            nxt = show.get('next', None)

            if nxt and self._compDeltaIn(
                    nxt['date'].date(), minDelta, maxDelta
            ):
                results.append((key, nxt))
                # self.debug("{} left: {}".format(key, nxt['date'].date() - now))
            if lat and self._compDeltaIn(
                    lat['date'].date(), minDelta, maxDelta
            ):
                results.append((key, lat))
                # self.debug("{} past: {}".format(key, lat['date'].date() - now))

        if self._showPath:
            try:
                self._saveJSONFile(
                    self._showPath,
                    self._shows,
                    pretty=True,
                    sort=True
                )
            except:
                self.exception("Failed to save shows")
        if self._showNamePath:
            try:
                self._saveJSONFile(
                    self._showNamePath,
                    sorted(self._shows.keys()),
                    pretty=True,
                    sort=True
                )
            except:
                self.exception("Failed to save show list")
        return results

