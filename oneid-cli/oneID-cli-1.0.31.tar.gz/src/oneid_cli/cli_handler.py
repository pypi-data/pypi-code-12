import argparse
import logging

from .services import Provision, ListProjects, CreateProject, Configure, Revoke, Show
from .session import CLISession

logger = logging.getLogger(__name__)


def main():
    session = CLISession()
    handler = CLIHandler(session)
    handler.main()


class CLIHandler(object):
    """
    Run service (provision, configure) with provided arguments

    :param session: Session instance for credentials and configuration
    :type session: session.CLISession

    :Example:

    $ oneid-cli configure --dev-id <unique-id>
                          --dev-secret <secret from developer portal>
                          --project <optional project id>
    """
    def __init__(self, session):
        self._command_table = None
        self._argument_table = None
        self._session = session

    def _get_command_table(self):
        """
        Build a list of arguments from the available commands
        """
        if self._command_table is None:
            # Map the service commands to classes
            self._command_table = {
                'configure': Configure(self._session),
                'list-projects': ListProjects(self._session),
                'create-project': CreateProject(self._session),
                'provision': Provision(self._session),
                'revoke': Revoke(self._session),
                'show': Show(self._session),
                # TODO: sign? -- could see for signing firmware update payloads to scp to devices
                #       check sig? -- not as likely, but maybe for checking downloaded data?
            }
        return self._command_table

    def main(self):
        parser = argparse.ArgumentParser(description='Run oneID Services from the command line')
        parser.add_argument('-d', '--debug',
                            choices=['NONE', 'INFO', 'DEBUG', 'WARNING', 'ERROR'],
                            default='NONE',
                            help='Specify level of debug output (default: %(default)s)')

        subparsers = parser.add_subparsers(title='Commands', dest='service')
        subparsers.required = True

        for cmd, handler in self._get_command_table().items():
            subparser = subparsers.add_parser(cmd)
            required_group = subparser.add_argument_group('required arguments')
            handler.setup_argparser(required_group, True)
            handler.setup_argparser(subparser, False)

            subparser.set_defaults(handler=handler)
            subparser.set_defaults(parser=subparser)

        try:
            args = parser.parse_args()

            self.set_logging_level(args.debug)
            logger.debug('args=%s', args)

            args.handler.run(args)

        except ValueError as e:
            logger.debug('Error running Service:', exc_info=True)
            print(e.message)

        except SystemExit:
            pass  # Service will have described the problem

        except:
            logger.warning('Error running service "%s"', args.service)
            logger.debug('Exception was:', exc_info=True)

    def set_logging_level(self, debug_level):
        level = getattr(logging, debug_level.upper(), 100)
        if not isinstance(level, int):
            raise ValueError('Invalid log level: %s' % debug_level)
        logging.basicConfig(level=level, format='%(asctime)-15s %(levelname)-8s [%(name)s:%(lineno)s] %(message)s')
