import os
import json
import logging

from collections import OrderedDict

from .base_loader import BaseLoader

logger = logging.getLogger(__name__)


class JSONLoader(BaseLoader):
    def __init__(self, filename, migrate=False):
        super(JSONLoader, self).__init__(filename)

        if migrate:
            print('Converting {}:'.format(filename))
            default_filename = self._migrate(filename)
            self._filename = default_filename
            print('Using {} as default configuration'.format(default_filename))

    def load_config(self):
        if os.stat(self.filename).st_size == 0:
            return {}
        with open(self.filename, 'rb') as fin:
            return json.load(fin, object_pairs_hook=OrderedDict)

    def save_config(self, config):
        with open(self.filename, 'w') as fout:
            json.dump(config, fout, sort_keys=False, indent=2)

    def _migrate(self, oldfile):
        ret = None
        olddata = None

        if os.stat(oldfile).st_size == 0:
            olddata = {}
        else:
            with open(oldfile, 'rb') as fin:
                olddata = json.load(fin)

        logger.debug('migrating %s', olddata)

        environments = OrderedDict()

        if 'DEFAULT' in olddata:
            logger.debug('loading default project: %s', olddata['DEFAULT'])
            environments['DEFAULT'] = self._convert_legacy_project_to_environment(olddata['DEFAULT'])
            environments['DEFAULT']['PROJECTS'] = OrderedDict()

        for project_id, project in olddata.items():
            if project_id == 'DEFAULT':
                continue
            logger.debug('loading legacy project: %s: %s', project_id, project)
            project_env = self._add_legacy_project_admin_to_environments(project, environments)
            self._add_legacy_project_to_projects(environments[project_env]['PROJECTS'], project_id, project)

        for env, config in environments.items():
            logger.debug('looping, ret=%s, env=%s, config=%s', ret, env, config)
            if env == 'DEFAULT':
                ret = newfile = oldfile + '.json'
            else:
                newfile = '{}-{}.json'.format(oldfile, env)

            with open(newfile, 'w') as fout:
                print('  {}'.format(newfile))
                logger.debug('Writing %s...', newfile)
                json.dump(config, fout, sort_keys=False, indent=2)
        return ret or oldfile + '.json'

    def _add_legacy_project_admin_to_environments(self, project, environments):
        project_env = self._find_matching_environment(project, environments)
        logger.debug('  project_env=%s', project_env)
        if not project_env:
            project_env = 'DEFAULT'
            counter = 1
            while project_env in environments:
                project_env = 'unknown_{}'.format(counter)
                counter += 1
            logger.debug('    now project_env=%s', project_env)

        if project_env in environments:
            self._update_environment_from_legacy_project(environments[project_env], project)
        else:
            environments[project_env] = self._convert_legacy_project_to_environment(project)
            environments[project_env]['PROJECTS'] = OrderedDict()
        return project_env

    def _find_matching_environment(self, legacy_project, environments):

        for env, environment in environments.items():
            project_admin = environment['PROJECT_ADMIN']
            logger.debug('seeing if env %s matches project %s', project_admin, legacy_project)

            if (project_admin and ('ID' not in legacy_project or 'ID' not in project_admin or project_admin['ID'] == legacy_project['ID']) and
                ('SECRET' not in legacy_project or 'SECRET' not in project_admin or project_admin['SECRET'] == legacy_project['SECRET']) and
                ('RETURN_KEY' not in legacy_project or 'RETURN_KEY' not in project_admin or
                    project_admin['RETURN_KEY'] == legacy_project['RETURN_KEY'])):

                logger.debug('  match')
                return env

        return None

    def _convert_legacy_project_to_environment(self, project):
        return {
            'PROJECT_ADMIN': OrderedDict([(key, project[key]) for key in ['ID', 'SECRET', 'RETURN_KEY'] if key in project])
        }

    def _update_environment_from_legacy_project(self, environment, project):
        project_admin = environment['PROJECT_ADMIN']

        for key in ['ID', 'SECRET', 'RETURN_KEY']:
            if not project_admin.get(key) and project.get(key):
                project_admin[key] = project[key]

    def _add_legacy_project_to_projects(self, projects, project_id, project):
        projects[project_id] = {
            'AES': project.get('AES')
        }
