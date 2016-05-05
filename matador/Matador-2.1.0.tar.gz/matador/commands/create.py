from .command import Command
from matador.session import Session
from matador import git
from pathlib import Path
from cookiecutter.main import cookiecutter


class CreateProject(Command):

    def __init__(self):
        super(CreateProject, self).__init__(init_session=False)

    def _add_arguments(self, parser):
        parser.prog = 'matador init'

        parser.add_argument(
            '-p', '--project',
            type=str,
            required=True,
            help='Project name')

    def _execute(self):
        cookiecutter(
            'https://github.com/Empiria/matador-cookiecutter.git',
            no_input=True,
            extra_context={'project_name': self.args.project})


class CreateTicket(Command):

    def _add_arguments(self, parser):
        parser.prog = 'matador create-ticket'

        parser.add_argument(
            '-t', '--ticket',
            type=str,
            required=True,
            help='Ticket name')

    def _execute(self):
        ticket_folder = Path(
            Session.project_folder, 'deploy', 'tickets', self.args.ticket)
        Path.mkdir(ticket_folder, parents=True, exist_ok=True)
        deploy_file = Path(ticket_folder, 'deploy.py')

        with deploy_file.open('w') as f:
            f.write('from matador.commands.deployment import *\n\n')
            f.close()

        git.stage_file(Session.project_repo, deploy_file)
        git.commit(Session.project_repo, 'Create ticket %s' % self.args.ticket)


class CreatePackage(Command):

    def _add_arguments(self, parser):
        parser.prog = 'matador create-package'

        parser.add_argument(
            '-p', '--package',
            type=str,
            required=True,
            help='Ticket name')

    def _execute(self):
        package_folder = Path(
            Session.project_folder, 'deploy', 'packages', self.args.package)
        Path.mkdir(package_folder, parents=True, exist_ok=True)

        package_file = Path(package_folder, 'tickets.yml')
        with package_file.open('w') as f:
            f.write(
                '# List each ticket on a separate line preceded by - . e.g.\n')
            f.write('# - 30\n')
            f.write('# - 31\n')
            f.close()
        git.stage_file(Session.project_repo, package_file)

        remove_file = Path(package_folder, 'remove.py')
        with remove_file.open('w') as f:
            f.write('from matador.commands.deployment import *\n\n')
            f.close()
        git.stage_file(Session.project_repo, remove_file)

        git.commit(
            Session.project_repo, 'Create package %s' % self.args.package)


class AddTicketToPackage(Command):

    def _add_arguments(self, parser):
        parser.prog = 'matador add-t2p'

        parser.add_argument(
            '-t', '--ticket',
            type=str,
            required=True,
            help='Ticket name')

        parser.add_argument(
            '-p', '--package',
            type=str,
            required=True,
            help='Ticket name')

    def _execute(self):
        package_file = Path(
            Session.project_folder, 'deploy', 'packages', self.args.package,
            'tickets.yml')

        with package_file.open('a') as f:
            f.write('- %s\n' % self.args.ticket)
            f.close()

        git.stage_file(Session.project_repo, package_file)
        git.commit(Session.project_repo, 'Add ticket %s to package %s' % (
                self.args.ticket, self.args.package))
