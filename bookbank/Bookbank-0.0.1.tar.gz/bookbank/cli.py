
import bookbank
import logging

from cliff.app import App
from cliff.commandmanager import CommandManager


class BookbankApp(App):
    """ Bookbank main command line interface definition    """
    def __init__(self):
        super(BookbankApp, self).__init__(
            description=bookbank.__desc__,
            version=bookbank.__version__,
            command_manager=CommandManager('bookbank.commands'),
            deferred_help=True,
            )

    def initialize_app(self, argv):
        self.LOG.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.LOG.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.LOG.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.LOG.debug('got an error: %s', err)

