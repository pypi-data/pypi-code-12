import os
import json
import base64
import logging

import oneid.keychain
import oneid.service

from .base import Service
from .. import util, session, config_file

logger = logging.getLogger(__name__)


class CreateProject(Service):
    """
    Start a new Project with keys
    Configuration will be updated with new Project data

    :Example:

        $ oneid-cli create-project --name my-iot-project --aes-key ae5f6d

    """
    def setup_argparser(self, parser, required=False):
        if required:
            parser.add_argument('--name', '-n', required=True, help='The name of the Project')
        else:
            parser.add_argument('--aes-key', help='base64-encoded AES encryption key (if not specified, one will be generated)')
            parser.add_argument('--output-dir', '-o', help='Directory to write Project keys directory to')
            parser.add_argument('--public-key', help='DER formatted public key')

    def _create_project(self, project_name, aes_key, project_keypair):
        """
        Create a new Project

        :param project_name: Server or Device name.
        :returns: created Project fields
        :rtype: dict
        :raises :py:class:session.HTTPException: Raised if there are any connection errors
        """
        project = None

        api_endpoint = session.PROJECTS_ENDPOINT

        public_key_b64 = base64.b64encode(project_keypair.public_key_der)

        keys = {'project': public_key_b64}
        description = oneid.service.encrypt_attr_value(project_name, aes_key)
        project_admin_id = self._session.keypair.identity
        project_admins = [project_admin_id]

        try:
            response = self._session.make_api_call(api_endpoint, 'POST',
                                                   description=json.dumps(description),
                                                   project_admins=project_admins,
                                                   public_keys=json.dumps(keys),
                                                   project=self._session.project)
            logger.debug(response)

            project = response and response.get('Projects', response)

            if project:
                description = json.loads(project['description'])

                try:
                    project['description'] = oneid.service.decrypt_attr_value(description, aes_key)
                except:
                    logger.debug('Exception decrypting freshly-saved Project description', exc_info=True)
                    project['description'] = '(encrypted)'

                project['public_keys'] = json.loads(project['public_keys'])

                print('Successfully Added Project: {id}: {description}'.format(**project))

                with config_file.update(project['id']) as configuration:  # pragma: nocover
                    configuration['AES'] = base64.b64encode(aes_key)
            else:
                print('Error creating Project')
                return None

        except session.HTTPException:
            logger.warning('Error Communicating with oneID - %s', api_endpoint, exc_info=True)
            print('Unable to process request -- Error Communicating with oneID')

        return project

    def _save_keys(self, output_dir, project_id, oneid_keypair, project_keypair):
        directory = os.path.join(output_dir, 'project-' + project_id)
        if not os.path.exists(directory):
            os.makedirs(directory)
        basename = os.path.join(directory, 'project-' + project_id)
        with open(basename + '-oneid-pub.pem', 'w') as f:
            f.write(oneid_keypair.public_key_pem)

        if project_keypair:
            with open(basename + '-priv.pem', 'w') as f:
                f.write(project_keypair.secret_as_pem)
            with open(basename + '-pub.pem', 'w') as f:
                f.write(project_keypair.public_key_pem)

        print('Keys saved to "{}"'.format(directory))

    def _print_keys(self, oneid_keypair, project_keypair):
        print('\noneID Project Public Key:\n')
        print(oneid_keypair.public_key_pem)
        raw_input('\nSave contents above, hit "Enter" to continue...')

        if project_keypair:
            print('\nProject Public Key:\n')
            print(project_keypair.public_key_pem)
            raw_input('\nSave contents above, hit "Enter" to continue...')

            print('\nProject Private Key:\n')
            print(project_keypair.secret_as_pem)
            print('\nSAVE CONTENTS ABOVE IN A SECURE LOCATION.')
            raw_input('Hit "Enter" to continue...')

    def run(self, args):
        """
        Create a project.

        :param args: command line argument parser args
        """
        aes_key = None
        if args.aes_key:
            aes_key = base64.b64decode(args.aes_key)
        else:
            aes_key = oneid.service.create_aes_key()

        project_keypair = None
        if args.public_key:
            # TODO: Specify public key type
            project_keypair = oneid.keychain.Keypair.from_public_der(base64.b64decode(args.public_key))
        else:
            print('No public key specified.')
            project_keypair = util.prompt_to_create_keypair()

        if not project_keypair:
            print('No public key given or generated. Unable to create "{}"'.format(args.name))
            return

        project = self._create_project(args.name, aes_key, project_keypair)

        if project:
            output_project_keypair = project_keypair if not args.public_key else False
            oneid_keypair = oneid.keychain.Keypair.from_public_der(base64.b64decode(project['public_keys']['oneid_project']))

            if args.output_dir:
                try:
                    self._save_keys(args.output_dir, project['id'], oneid_keypair, output_project_keypair)
                except EnvironmentError as e:
                    print('Error saving keys: {}'.format(e))
            else:
                self._print_keys(oneid_keypair, output_project_keypair)
