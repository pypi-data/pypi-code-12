from datetime import datetime, timedelta

from sqlalchemy import Column, String, Integer, Boolean

from sqlpharmacy.core import Database

from tek.tools import unix_to_datetime, datetime_to_unix
from series.logging import Logging
from golgi.config import configurable


@configurable(show_planner=['show_db'])
class Show(Logging, metaclass=Database.DefaultMeta):
    rage_id = Column(String)
    etvdb_id = Column(String)
    name = Column(String)
    canonical_name = Column(String)
    latest_season = Column(Integer)
    latest_episode = Column(Integer)
    season = Column(Integer)
    next_episode = Column(Integer)
    next_episode_stamp = Column(Integer)
    last_check_stamp = Column(Integer)
    ended = Column(Boolean)

    def __init__(self, **kw):
        self.rage_id = ''
        self.etvdb_id = ''
        self.name = ''
        self.next_episode_stamp = 0
        self.last_check_stamp = 0
        self.season = -1
        self.latest_episode = -1
        self.latest_season = -1
        self.next_episode = -1
        self.ended = False
        super().__init__(**kw)

    def __str__(self):
        return 'Show "{}"({}), {}x{}, {}x{}'.format(
            self.name,
            self.tvdb_id,
            self.latest_season,
            self.latest_episode,
            self.season,
            self.next_episode
        )

    def __repr__(self):
        return '<Show({}, {}, {}x{}, {}x{})'.format(
            self.name,
            self.tvdb_id,
            self.latest_season,
            self.latest_episode,
            self.season,
            self.next_episode
        )

    @property
    def next_episode_date(self):
        return unix_to_datetime(self.next_episode_stamp or 0)

    @next_episode_date.setter
    def next_episode_date(self, date):
        try:
            self.next_episode_stamp = datetime_to_unix(date)
        except Exception as e:
            self.log.error('Could not set episode date: {}'.format(e))

    @property
    def last_check(self):
        return unix_to_datetime(self.last_check_stamp or 0)

    @last_check.setter
    def last_check(self, date):
        self.last_check_stamp = datetime_to_unix(date)

    @property
    def has_next_episode(self):
        return (self.next_episode_stamp is not None and
                self.next_episode > 0 and
                self.next_episode_date > datetime.now() - timedelta(days=1))

    def can_recheck(self, threshold):
        return (datetime.now() - self.last_check).total_seconds() > threshold

    @property
    def current_episode_enum(self):
        if self.next_episode_imminent:
            return (self.season, self.next_episode)
        else:
            return (self.latest_season, self.latest_episode)

    @property
    def current_episode(self):
        return self.current_episode_enum[1]

    @property
    def current_season(self):
        return self.season if self.season > 0 else self.latest_season

    @property
    def next_episode_imminent(self):
        return (self.has_next_episode and self.next_episode_date <
                datetime.now() + timedelta(days=1))

    @property
    def tvdb_id(self):
        return self.etvdb_id if self._show_db == 'etvdb' else self.rage_id

    @property
    def info(self):
        return dict(
            name=self.name,
            season=self.season,
            next_episode=self.next_episode_date.strftime('%F'),
        )

__all__ = ['Show']
