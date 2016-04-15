import json
import logging

import oneid.service
import oneid.utils

from .base import Service, add_project_id_param
from .. import session, config_file

logger = logging.getLogger(__name__)


class ListProjects(Service):
    """
    List the Projects that you are assigned to. If a specific `project_id` is given,
    the details of that Project will be printed.

    :Example:

        $ oneid-cli list-projects

        or

        $ oneid-cli list-projects --project-id 720c645b-0873-44f5-aafe-2d7a4d81be8e

    """
    def setup_argparser(self, parser, required=False):
        if not required:
            add_project_id_param(parser, False)

    def _list_projects(self):
        """
        List all the Projects, one per line
        """
        try:
            response = self._session.make_api_call(session.PROJECTS_ENDPOINT, 'GET')
            logger.debug(response)
            projects = response and response.get('Projects', response)

            if not response:
                print('No Projects found.')
                return

            for project in projects:
                with config_file.load(project['id']) as config:
                    key = config and 'AES' in config and oneid.utils.base64url_decode(config['AES'])
                    description = json.loads(project['description'])
                    description = oneid.service.decrypt_attr_value(description, key) if key else '(encrypted)'
                    status = '(REVOKED)' if project['revocation_status'] == 'REV' else ''
                    print("{}: {} {}".format(project['id'], description, status))  # pragma: nocover -- no idea why this is needed

        except session.HTTPException:
            logger.warning('Error Communicating with oneID - %s', session.PROJECTS_ENDPOINT, exc_info=True)

    def _list_project(self, project_id):
        """
        List the details of a given Project

        :param project_id: The Project to detail
        """
        try:
            response = self._session.make_api_call(session.PROJECT_ENDPOINT.format(project_id=project_id), 'GET')
            project = response.get('Projects', response)

            logger.debug(project)

            if not project:
                print('Project "{}" not found'.format(project_id))
                return

            with config_file.load(project['id']) as config:
                key = None
                if config and 'AES' in config:
                    key = oneid.utils.base64url_decode(config['AES'])
                    description = json.loads(project['description'])
                    description = oneid.service.decrypt_attr_value(description, key)
                else:
                    description = '(encrypted)'
                status = '(REVOKED)' if project['revocation_status'] == 'REV' else ''
                print("{}: {} {}".format(project['id'], description, status))
                self._print_project_admins(project, key)
                self._print_servers(project, key)
                self._print_edge_devices(project, key)  # pragma: nocover -- no idea why this is needed

        except session.HTTPException:
            logger.warning('Error Communicating with oneID - %s', session.PROJECTS_ENDPOINT, exc_info=True)
            print('Unable to process request -- Error Communicating with oneID')

    def _print_project_admins(self, project, key, prefix='  '):
        print('{}Project Admins:'.format(prefix))

        for projects_admin_id in project['project_admins']:
            print('{}  {}'.format(prefix, projects_admin_id))

    def _print_servers(self, project, key, prefix='  '):
        print('{}Servers:'.format(prefix))

        response = self._session.make_api_call(session.SERVERS_ENDPOINT.format(project_id=project['id']), 'GET')
        servers = response.get('Servers', response)

        logger.debug(servers)

        for server in servers:
            description = json.loads(server['description'])
            description = oneid.service.decrypt_attr_value(description, key) if key else '(encrypted)'
            status = '(REVOKED)' if server['revocation_status'] == 'REV' else ''
            print("{}  {}: {} {}".format(prefix, server['id'], description, status))

    def _print_edge_devices(self, project, key, prefix='  '):
        print('{}Edge Devices:'.format(prefix))

        response = self._session.make_api_call(session.EDGE_DEVICES_ENDPOINT.format(project_id=project['id']), 'GET')
        edge_devices = response.get('EdgeDevices', response)

        logger.debug(edge_devices)

        for edge_device in edge_devices:
            description = json.loads(edge_device['description'])
            description = oneid.service.decrypt_attr_value(description, key) if key else '(encrypted)'
            status = '(REVOKED)' if edge_device['revocation_status'] == 'REV' else ''
            print("{}  {}: {} {}".format(prefix, edge_device['id'], description, status))

    def run(self, args):
        """
        Execute the :py:class:`ListProjects` service functions

        :param args: command line argument parser args
        """
        if args.project_id:
            self._session.project = args.project_id
            self._list_project(args.project_id)
        else:
            self._list_projects()
