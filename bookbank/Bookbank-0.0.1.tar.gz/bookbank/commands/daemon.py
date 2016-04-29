from cliff.commandmanager import CommandManager
from cliff.command import Command


class Daemon(Command):
    "Runs Bookbank as a daemon"

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        self.log.info('sending greeting')
        self.log.debug('debugging')
        self.app.stdout.write('hi!\n')
