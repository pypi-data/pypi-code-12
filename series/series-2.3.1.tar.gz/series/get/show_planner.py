from datetime import datetime

from series.get.handler import ShowHandler
from series.get.tvdb import Tvdb

from tek.config import configurable
from tek import logger


@configurable(series=['monitor'], show_planner=['check_interval', 'show_db'])
class ShowPlanner(ShowHandler, Tvdb):

    def __init__(self, releases, shows, *a, **kw):
        super().__init__(shows, 5, 'show planner', *a,
                                          **kw)
        self._releases = releases
        self._shows_initialized = False

    def _sanity_check(self):
        if not self._shows_initialized:
            self._init()

    def _init(self):
        for name in self._monitor:
            self._init_show(name)
        self._shows_initialized = True

    def _init_show(self, name):
        if not self._shows.name_exists(name):
            self._add_show(name)

    def _add_show(self, name):
        logger.debug('Adding show for "{}"'.format(name))
        show = self.tvdb.show(name)
        if show:
            self._shows.add(name, show)
        else:
            logger.debug('Adding show failed.')

    def _handle(self, show):
        show.last_check = datetime.now()
        rage = self.tvdb.show(show.name, show.tvdb_id)
        if rage is None:
            logger.error(
                'Show couldn\'t be found anymore: {}'.format(show.name)
            )
        else:
            self._update_show(show, rage)

    def _update_show(self, show, rage):
        logger.debug('Updating show {}'.format(rage.name))
        data = {}
        if rage.ended:
            data['ended'] = True
            logger.warn('Show has ended: {}'.format(show.name))
        else:
            data = self._fetch_next_episode(show, rage)
        if show.tvdb_id is None:
            data.update(**self.tvdb.show_id_update_param(show))
        self._shows.update(show.id, data)

    def _fetch_next_episode(self, show, rage):
        data = {}
        logger.debug('Fetching next episode for "{}"'.format(show.name))
        latest = rage.latest_episode
        if latest is not None:
            data.update(latest_episode=latest.number,
                        latest_season=latest.season)
        date = self.tvdb.next_episode_date(rage)
        if date is not None:
            data['next_episode_date'] = date
            enum = self.tvdb.next_episode_enum(rage)
            data['season'], data['next_episode'] = enum
            logger.debug('Found season {} episode {}'.format(*enum))
        else:
            logger.debug('Fetching next episode failed.')
        return data

    def _qualify(self, show):
        return (not show.has_next_episode and not show.ended
                and show.can_recheck(self._check_interval))

__all__ = ['ShowPlanner']
