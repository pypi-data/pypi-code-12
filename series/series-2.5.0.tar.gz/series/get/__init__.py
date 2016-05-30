from tek import configurable

from tryp import _, __

from series.get.releases_facade import ReleasesFacade
from series.get.db import FileDatabase
from series.app import App
from series.get.shows_facade import ShowsFacade
from series.handler import Handler
from series.get.rest_api import RestApi


@configurable(get=['db_path', 'run', 'omit', 'auto_upgrade_db'])
class SeriesGetD(App):
    components = ['feed_poller', 'downloader', 'archiver', 'subsyncer',
                  'rest_api', 'link_handler', 'torrent_handler',
                  'library_handler', 'show_planner', 'torrent_finder',
                  'show_scheduler']

    def __init__(self):
        self._setup_db()
        super().__init__(
            'get', self._run, self._omit,
            c_args=(self.releases, self.shows), name='SeriesGetD'
        )
        self.rest_api = self._components.find(lambda a: isinstance(a, RestApi))
        self.rest_api.foreach(__.set_daemon(self))

    def _setup_db(self):
        self.db = FileDatabase(self._db_path,
                               auto_upgrade=self._auto_upgrade_db)
        self.releases = ReleasesFacade(self.db)
        self.shows = ShowsFacade(self.db)

    def load_monitors(self):
        count = self.releases.count
        self.log.info('Loaded {} releases from db.'.format(count))

    def tick(self):
        pass

    def prepare(self):
        self.load_monitors()

    def _cleanup(self):
        self.db.commit()
        self.db.disconnect()

    def activate_release(self, id):
        for c in self._components:
            if isinstance(c, Handler):
                c.activate_id(id)

__all__ = ['SeriesGetD']
