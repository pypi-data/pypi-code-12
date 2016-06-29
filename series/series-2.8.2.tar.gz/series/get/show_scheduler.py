from datetime import datetime, timedelta
from typing import Callable

from series.get.handler import ShowHandler, S
from series.get.tvdb import Tvdb

from series.condition import HandlerCondition, DynCondition, SimpleCondition
from series.get.model.show import Show
from series.get import ReleaseMonitor


class AirsToday(HandlerCondition):

    def ev(self, show):
        return (show.has_next_episode and
                show.next_episode_date < datetime.now() + timedelta(days=1))

    def describe(self, show, target):
        match = self.ev(show)
        good = match == target
        today = (show.next_episode_date > datetime.now()) and match
        desc = ('today' if today else
                show.next_episode_date.strftime('%F') if
                show.next_episode_stamp > 0 else
                'no date')
        return 'airs today[{}]'.format(self._paint(desc, good))


class CanCatchUp(SimpleCondition):

    def __init__(self, latest) -> None:
        self._latest = latest

    def current(self, show):
        return show.current_episode

    def latest(self, show):
        return self._latest(show).episode

    def ev(self, show):
        return self.current(show) > self.latest(show)

    @property
    def _desc(self):
        return 'latest > watched'

    def _repr(self, show, match):
        op = '>' if match else '<'
        return '{} {} {}'.format(self.current(show), op, self.latest(show))


class CanSchedule(DynCondition):

    def __init__(self, latest: Callable[[Show], ReleaseMonitor]) -> None:
        self._latest = latest

    def _dyn_sub(self, show):
        if self._latest(show) is None:
            return (S('has_next_episode') & AirsToday())
        else:
            return CanCatchUp(self._latest)

    def describe(self, show, target):
        s = super().describe(show, target)
        pre = 'fresh' if self._latest(show) is None else 'continuing'
        return '{} show => {}'.format(pre, s)


class ShowScheduler(ShowHandler, Tvdb):

    def __init__(self, releases, shows, **kw):
        super().__init__(shows, 5, 'show scheduler', cooldown=3600, **kw)
        self._releases = releases

    def _handle(self, show):
        latest = self._latest(show)
        if latest is None:
            self._schedule(show, show.season, show.next_episode)
        else:
            for episode in range(latest.episode + 1, show.current_episode + 1):
                self._schedule(show, show.current_season, episode)

    @property
    def _conditions(self):
        return CanSchedule(self._latest)

    def _latest(self, show):
        return self._releases.latest_for_season(show.canonical_name,
                                                show.current_season)

    def _schedule(self, show, season, episode):
        airdate = self.tvdb.airdate(show, season, episode)
        msg = 'Scheduling release "{} {}x{}" on {}'.format(
            show.name,
            season,
            episode,
            airdate
        )
        self.log.info(msg)
        self._releases.create(show.canonical_name, season, episode, airdate)
        self._commit()

__all__ = ['ShowScheduler']
