import os
import json
import base64
import logging

import oneid.keychain
import oneid.service

from .base import Service, add_project_id_param, add_device_type_params
from .. import util, session

logger = logging.getLogger(__name__)


class Provision(Service):
    """
    Provision a new device with keys

    :Example:

        $ oneid-cli provision --type edge_device --name my-iot-device --public-key abcdefg

    """
    def setup_argparser(self, parser, required=False):
        if required:
            parser.add_argument('--name', '-n', required=True, help='The name of the device')
            add_project_id_param(parser)
            add_device_type_params(parser)
        else:
            parser.add_argument('--output-dir', '-o', help='Directory to write keys to')
            parser.add_argument('--public-key', help='DER formatted public key')

    def _add_entity_to_project(self, entity_type, entity_name, device_keypair):
        """
        Provision a device to the specified project

        :param entity_type: Either a server or device.
        :param entity_name: Server or Device name.
        :param device_keypair: Keypair for oneID to later validate the entity signature.
        :raises HTTPError: Raised if there are any connection errors
        """
        provisioning_endpoint = session.SERVERS_ENDPOINT.format(project_id=self._session.project)
        if entity_type == 'edge_device':
            provisioning_endpoint = session.EDGE_DEVICES_ENDPOINT.format(project_id=self._session.project)

        public_key_b64 = base64.b64encode(device_keypair.public_key_der)

        keys = {entity_type: public_key_b64}
        entity_description = oneid.service.encrypt_attr_value(entity_name,
                                                              self._session.encryption_key)

        try:
            response = self._session.make_api_call(provisioning_endpoint,
                                                   'POST',
                                                   description=json.dumps(entity_description),
                                                   public_keys=json.dumps(keys),
                                                   project=self._session.project)
            logger.debug(response)

            if not response:
                print('Error provisioning {}'.format(entity_type))
                return

            print('Successfully Added {entity_type}: {entity_name}'.format(entity_type=entity_type,
                                                                           entity_name=entity_name))

            resourceName = ''.join(word.capitalize() for word in entity_type.split('_')) + 's'
            return response[resourceName] if resourceName in response else response

        except session.HTTPException:
            logger.warning('Error Communicating with oneID - %s' % provisioning_endpoint, exc_info=True)
            print('Unable to process request -- Error Communicating with oneID')

    def _save_keys(self, output_dir, project_id, device_id, device_type, entity_keypair, project_device_keypair):
        directory = os.path.join(output_dir, 'project-' + project_id, device_type + '-' + device_id)
        if not os.path.exists(directory):
            os.makedirs(directory)
        basename = os.path.join(directory, device_type + '-' + device_id)

        if entity_keypair:
            logger.debug('opening: %s', basename + '-oneid-priv.pem')
            with open(basename + '-oneid-priv.pem', 'w') as f:
                f.write(entity_keypair.secret_as_pem)
            with open(basename + '-oneid-pub.pem', 'w') as f:
                f.write(entity_keypair.public_key_pem)

        if project_device_keypair:
            with open(basename + '-project-priv.pem', 'w') as f:
                f.write(project_device_keypair.secret_as_pem)
            with open(basename + '-project-pub.pem', 'w') as f:
                f.write(project_device_keypair.public_key_pem)
        print('Keys saved to "{}"'.format(directory))

    def _print_keys(self, entity_keypair, project_device_keypair):

        if entity_keypair:
            print('\nEntity oneID Public Key:\n')
            print(entity_keypair.public_key_pem)
            raw_input('\nSave contents above, hit "Enter" to continue...')

            print('\nEntity oneID Private Key:\n')
            print(entity_keypair.secret_as_pem)
            print('\nSAVE CONTENTS ABOVE IN A SECURE LOCATION.')
            raw_input('Hit "Enter" to continue...')

        if project_device_keypair:
            print('\nProject Public Key:\n')
            print(project_device_keypair.public_key_pem)
            raw_input('\nSave contents above, hit "Enter" to continue...')

            print('\nProject Private Key:\n')
            print(project_device_keypair.secret_as_pem)
            print('\nSAVE CONTENTS ABOVE IN A SECURE LOCATION.')
            raw_input('Hit "Enter" to continue...')

    def run(self, args):
        """
        Provision a device with a set of identity and application keys.
        If output not specified, print to console
        If public key not specified, generate a private key and save to output

        :param args: command line argument parser args
        """
        self._session.project = args.project_id

        device_keypair = None
        if args.public_key:
            # TODO: Specify public key type
            device_keypair = oneid.keychain.Keypair.from_public_der(base64.b64decode(args.public_key))
        else:
            print('No public key specified.')
            device_keypair = util.prompt_to_create_keypair()

        if not device_keypair:
            print('No public key given or generated. Unable to create "{}"'.format(args.name))
            return

        entity = self._add_entity_to_project(args.type, args.name, device_keypair)

        if entity:
            output_entity_keypair = device_keypair if not args.public_key else False
            project_entity_keypair = None
            if args.type != 'server':
                print('You will also need Project keys for this entity.')
                project_entity_keypair = util.prompt_to_create_keypair()

            if output_entity_keypair or project_entity_keypair:
                if args.output_dir:
                    try:
                        self._save_keys(args.output_dir, entity['project'], entity['id'], args.type, output_entity_keypair, project_entity_keypair)
                    except EnvironmentError as e:
                        print('Error saving keys: {}'.format(e))
                else:
                    self._print_keys(output_entity_keypair, project_entity_keypair)
