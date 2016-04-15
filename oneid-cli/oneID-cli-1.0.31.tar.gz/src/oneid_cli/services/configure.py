import logging

from .. import config_file
from .base import Service, add_project_id_param

logger = logging.getLogger(__name__)


class Configure(Service):
    """
    Store json dump of credentials in ~/.oneid/credentials

    :Example:

        $ oneid-cli configure

    """
    def setup_argparser(self, parser, required=False):
        if not required:
            add_project_id_param(parser, False)

    def update_project_credentials(self, project_id, aes_key):
        """
        Create or update stored Project configuration data

        :param project_id: Project to update
        :param aes_key: Project's encryption key, base64-encoded (non-URL-safe) DER-formatted AES256 key
        :type project_id: str()
        :type aes_key: str()
        """
        with config_file.update(project_id) as credentials:
            credentials['AES'] = aes_key

    def update_project_admin_credentials(self, project_admin_id, access_secret, return_key):
        """
        Create or update stored ProjectAdmin configuration data

        :param project_admin_id: oneID Developer portal ID for the project admin
        :param access_secret: ProjectAdmin's secret key, DER-formatted private key
        :type project_admin_id: str()
        :type access_secret: str()
        """
        if project_admin_id is None or access_secret is None:
            raise ValueError('Access ID and Access Secret are required to configure')

        with config_file.update() as config:
            credentials = config.get('PROJECT_ADMIN', {})
            credentials['ID'] = project_admin_id
            credentials['SECRET'] = access_secret
            credentials['RETURN_KEY'] = return_key

            config['PROJECT_ADMIN'] = credentials

    def run(self, args):
        project_id = args.project_id
        if project_id:
            project_encryption_key = raw_input('PROJECT ENCRYPTION KEY: ')
            self.update_project_credentials(project_id, project_encryption_key)
        else:
            project_admin_id = raw_input('ONEID ACCESS ID: ')
            access_secret = raw_input('ONEID ACCESS SECRET: ')
            return_key = raw_input('ONEID ACCESS RETURN KEY: ')
            self.update_project_admin_credentials(project_admin_id, access_secret, return_key)
