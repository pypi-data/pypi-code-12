from series.get.handler import ShowHandler
from series.get.tvdb import Tvdb

from series.logging import Logging


class ShowScheduler(ShowHandler, Tvdb):

    def __init__(self, releases, shows, **kw):
        super().__init__(shows, 5, 'show scheduler',
                                            cooldown=3600, **kw)
        self._releases = releases

    def _handle(self, show):
        latest = self._latest(show)
        if latest is None:
            self._schedule(show, show.season, show.next_episode)
        else:
            for episode in range(latest.episode + 1, show.current_episode + 1):
                self._schedule(show, show.current_season, episode)

    def _qualify(self, show):
        latest = self._latest(show)
        if latest is None:
            return show.next_episode_imminent
        else:
            return show.current_episode > latest.episode

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
