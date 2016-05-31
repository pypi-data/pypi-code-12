from tek import configurable

from series.library.db import FileDatabase
from series.library.library_facade import LibraryFacade
from series.library.player import Player
from series.app import App


@configurable(library=['db_path', 'run', 'omit'])
class SeriesLibraryD(App):
    components = ['rest_api', 'metadata']

    def __init__(self):
        self.db = FileDatabase(self._db_path)
        self._library = LibraryFacade(self.db)
        self._player = Player(self._library)
        super().__init__('library', self._run, self._omit,
                                             c_args=(self._library,
                                                     self._player),
                                             name='SeriesLibD')

    def tick(self):
        pass

    def _cleanup(self):
        self.db.session.commit()
        self.db.disconnect()

__all__ = ['SeriesLibraryD']
