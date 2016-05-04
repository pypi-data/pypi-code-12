#!/usr/bin/env python
from pathlib import Path
from matador.session import Session
from .deployment import DeploymentCommand
from matador.commands.run_sql_script import run_sql_script
from matador import git


def _fetch_script(repo, script_path, commit_ref, target_folder):
    script = Path(repo.path, script_path)
    target_script = Path(target_folder, script.name)

    git.checkout(repo, commit_ref)

    with script.open('r') as f:
        original_text = f.read()
        f.close()

    new_text = git.substitute_keywords(original_text, repo, commit_ref)

    with target_script.open('w') as f:
        f.write(new_text)
        f.close()

    return target_script


class DeploySqlScript(DeploymentCommand):

    def _execute(self):
        path = Path(self.args[0])

        if str(path.parent) == '.':
            script = Path(Session.deployment_folder, path)
        else:
            commit = self.args[1]
            script = _fetch_script(
                Session.matador_repo, path, commit, Session.deployment_folder)

        kwargs = {
            **Session.environment['database'],
            **Session.credentials
        }

        kwargs['directory'] = str(script.parent)
        kwargs['file'] = str(script.name)

        run_sql_script(self._logger, **kwargs)


class DeployOraclePackage(DeploymentCommand):

    def _execute(self):
        package_name = self.args[0]
        commit = self.args[1]

        repo_folder = Session.matador_repository_folder
        package_folder = Path(
            repo_folder, 'src', 'db_objects', 'packages', package_name)
        package_spec = Path(package_folder, package_name + '.pks')
        package_body = Path(package_folder, package_name + '.pkb')

        spec_script = _fetch_script(
            Session.matador_repo, package_spec, commit,
            Session.deployment_folder)
        body_script = _fetch_script(
            Session.matador_repo, package_body, commit,
            Session.deployment_folder)

        run_sql_script(self._logger, spec_script)
        run_sql_script(self._logger, body_script)
