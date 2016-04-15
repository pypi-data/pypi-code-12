import logging

from .. import util

logger = logging.getLogger(__name__)


class Service(object):
    """
    Base Service that all services subclass

    :param session: session that manages the current user's
      credentials and settings
    :type session: session.CLISession
    """
    request_uri = None

    def __init__(self, active_session):
        self._session = active_session

    def setup_argparser(self, parser, required=False):
        """
        oneid-cli will create the main argument parser and subparsers
        each Service will be able to specify additional, Service-specific arguments, if needed
        """
        pass

    def run(self, *args):
        """
        oneid-cli will first parse for the service
        if a valid service is found, it will pass the remaining
        args to the service for the service to parse
        """
        logger.warning('Attempt to call unimplemented Service')
        raise NotImplementedError


# Some common parameters that can be shared across Services
#
def add_project_id_param(parser, required=True):
    parser.add_argument('--project-id', '-p', type=util.uuid_param, required=required, help='Specify a project using oneID project UUID')


def add_device_type_params(parser, required=True):
    parser.add_argument('--type', '-t', choices=['edge_device', 'server'], required=required, help='Type of device')
