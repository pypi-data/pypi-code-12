import bookbank
import logging

from cliff.command import Command

class Search(Command):
    "Search for book, paper, article or journal."

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        self.app.stdout.write('hi!\n')
