import logging

from .. import config_file
from .base import Service, add_project_id_param

logger = logging.getLogger(__name__)


class Show(Service):
    """
    Show project specific information through the command line
    """
    def setup_argparser(self, parser, required=False):
        if required:
            add_project_id_param(parser, True)
        else:
            parser.add_argument('--key', '-k', action='store_true', required=True)

    def run(self, args):
        """
        Show the information given the parameters passed in

        :param args: Command Line arguments
        :return: None
        """
        with config_file.load(args.project_id) as config:
            if config and 'AES' in config:
                key = config['AES']
                if args.key and key:
                    print(key)
