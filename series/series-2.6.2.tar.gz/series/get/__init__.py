from tek import configurable
from tek.io.terminal import terminal as term, ColorString

from tryp import __, List, Map

from series.get.releases_facade import ReleasesFacade
from series.get.db import FileDatabase
from series.app import App
from series.get.shows_facade import ShowsFacade
from series.handler import Handler
from series.get.model.release import ReleaseMonitor
from series.get.handler import ReleaseHandler


@configurable(get=['db_path', 'run', 'omit', 'auto_upgrade_db'])
class SeriesGetD(App):
    _components = ['feed_poller', 'downloader', 'archiver', 'subsyncer',
                   'rest_api', 'link_handler', 'torrent_handler',
                   'library_handler', 'show_planner', 'torrent_finder',
                   'show_scheduler']

    def __init__(self, db=None):
        self._setup_db(db)
        super().__init__(
            'get', self._run, self._omit,
            c_args=(self.releases, self.shows), name='SeriesGetD'
        )
        self.component_map.get('rest_api').foreach(__.set_getd(self))
        self.handlers = self.components.filter_type(Handler)
        self.release_handlers = self.handlers.filter_type(ReleaseHandler)

    def _setup_db(self, db):
        self.db = db or FileDatabase(self._db_path,
                                     auto_upgrade=self._auto_upgrade_db)
        self.releases = ReleasesFacade(self.db)
        self.shows = ShowsFacade(self.db)

    def load_monitors(self):
        count = self.releases.count
        self.log.info('Loaded {} releases from db.'.format(count))

    def prepare(self):
        self.load_monitors()

    def _cleanup(self):
        self.db.commit()
        self.db.disconnect()

    def activate_release(self, id):
        for c in self.release_handlers:
            c.activate_id(id)

    def explain(self, releases: List[ReleaseMonitor], services: List[str]):
        handlers = self.handlers if 'all' in services else (
            services.flat_map(self.component_map.get))
        expl = releases / __.explain / handlers.map
        return [dict(release=r.info, expl=e) for r, e in zip(releases, expl)]

    def format_explain(self, releases, services):
        return format_explain(self.explain(releases, services))


def explain_lines(data):
    def single(e):
        for comp in e:
            name = str(ColorString(comp['name'], term.blue))
            cond = comp['cond']
            yield '{}: {}'.format(name, cond)
    for r in data:
        release = Map(r['release']['release'])
        data = release.values_at('series', 'season', 'episode')
        name = '{} {}x{}'.format(*data)
        yield str(ColorString(name, term.bold))
        yield from single(r['expl'])
        yield ''


def format_explain(data):
    return '\n'.join(explain_lines(data))

__all__ = ['SeriesGetD']
