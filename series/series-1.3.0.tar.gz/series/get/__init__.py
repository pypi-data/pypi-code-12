from tek import logger, configurable

from series.get.releases_facade import ReleasesFacade
from series.get.db import FileDatabase
from series.app import App
from series.get.shows_facade import ShowsFacade


@configurable(get=['db_path', 'run', 'omit', 'auto_upgrade_db'])
class SeriesGetD(App):
    components = ['feed_poller', 'downloader', 'archiver', 'subsyncer',
                  'rest_api', 'link_handler', 'torrent_handler',
                  'library_handler', 'show_planner', 'torrent_finder',
                  'show_scheduler']

    def __init__(self):
        self._setup_db()
        super(SeriesGetD, self).__init__(
            'get', self._run, self._omit,
            c_args=(self.releases, self.shows), name='SeriesGetD'
        )

    def _setup_db(self):
        self.db = FileDatabase(self._db_path,
                               auto_upgrade=self._auto_upgrade_db)
        self.releases = ReleasesFacade(self.db)
        self.shows = ShowsFacade(self.db)

    def load_monitors(self):
        count = self.releases.count
        logger.info('Loaded {} releases from db.'.format(count))

    def tick(self):
        self.releases.check_commit()

    def prepare(self):
        self.load_monitors()

    def _cleanup(self):
        self.db.commit()
        self.db.disconnect()

__all__ = ['SeriesGetD']
