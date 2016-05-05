#!/usr/bin/env python3
"""
Mimir
Mimir CLI tool
COPYRIGHT 2016 MIMIR CORPORATION
"""
import os
import sys
import logging
import errno
import json
import zipfile
import getpass
import requests
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.command import Command
from cliff.complete import CompleteCommand

###GLOBALS
__version__ = "0.0.1"
API_URL = "https://dev.mimir.technology"
MIMIR_DIR = os.path.expanduser("~/.mimir/")
AUTH_SUCCESS = "Successfully logged into Mimir!\n"
ERR_NOT_AUTH = "Please log in first!\n"
ERR_INVALID_CRED = "Invalid email or password!\n"
ERR_INVALID_FILE = "Failed to open file.\n"
INPUT_FUNCTION = None
###GLOBALS

###ENV
#CHECK IF PYTHON 2 OR 3
if sys.version_info >= (3, 0):
    INPUT_FUNCTION = input
else:
    INPUT_FUNCTION = raw_input
logging.getLogger("requests").setLevel(logging.WARNING)
###ENV

###HELPER METHODS
def try_to_create_folder(path):
    """creates a folder if it doesnt exist"""
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def login(email, password):
    """logs into the platform api"""
    login_request = requests.post("{}/web/user_sessions".format(API_URL),
                                  data={"email": email, "password": password})
    data = json.loads(login_request.text)
    if data["success"]:
        authentication_token = data["auth_token"]
        write_credentials(authentication_token)
    return data["success"]

def read_credentials():
    """reads the user credentials from the mimir directory"""
    try_to_create_folder(MIMIR_DIR)
    credentials_path = "{}.credentials".format(MIMIR_DIR)
    if os.path.isfile(credentials_path):
        mimir_credentials_file = open(credentials_path, "r")
        return json.loads(mimir_credentials_file.read())
    else:
        return {}

def write_credentials(auth_token):
    """writes the user credentials to the mimir directory"""
    try_to_create_folder(MIMIR_DIR)
    credentials_path = "{}.credentials".format(MIMIR_DIR)
    mimir_credentials_file = open(credentials_path, "w")
    credentials = json.dumps({"auth_token": auth_token})
    mimir_credentials_file.write(credentials)
    mimir_credentials_file.close()

def continuous_prompt():
    """prompts for a login repeatedly"""
    while True:
        if prompt_login():
            return True
        else:
            sys.stderr.write("\n{}\n".format(ERR_INVALID_CRED))
    return False

def prompt_login():
    """prompts for a login"""
    email = INPUT_FUNCTION("Email: ")
    password = getpass.getpass()
    return login(email, password)

def get_projects_list():
    """gets the projects list for a user"""
    url = "{}/projects".format(API_URL)
    credentials = read_credentials()
    if "auth_token" in credentials:
        headers = {"Authorization": credentials["auth_token"]}
        projects_request = requests.get(url, headers=headers)
        result = json.loads(projects_request.text)
        return result["projects"]
    else:
        continuous_prompt()
        return get_projects_list()

def prompt_for_project(projects):
    """prompts for which project"""
    counter = 0
    for project in projects:
        sys.stdout.write("{}: {}\n".format(str(counter), project["name"]))
        counter += 1
    choice = -1
    while choice < 0 or choice >= len(projects):
        try:
            choice = int(INPUT_FUNCTION("Type the number of the project you want to submit to: "))
        except ValueError:
            sys.stderr.write("Input a number 0 through {} please!\n".format(str(len(projects)-1)))
    return projects[choice]

def zipdir(ziph, path):
    """zips a directory up for submission"""
    for _, _, files in os.walk(path):
        for file in files:
            ziph.write(file)

def submit(filename, project_id):
    """submits file(s) to the mimir platform"""
    url = "{}/projects/{}/project_submissions.json".format(API_URL, project_id)
    credentials = read_credentials()
    if "auth_token" in credentials:
        data = {"project_submission[project_id]": project_id}
        headers = {"Authorization": credentials["auth_token"]}
        submission_file = None
        if filename.lower().endswith(".zip"):
            submission_file = open(filename, "rb")
        else:
            zipfilename = "{}current_submission.zip".format(MIMIR_DIR)
            try:
                os.remove(zipfilename)
            except OSError:
                pass
            myzip = zipfile.ZipFile(zipfilename, 'w')
            if os.path.isdir(filename):
                zipdir(myzip, filename)
            else:
                myzip.write(filename)
            myzip.close()
            submission_file = open(zipfilename, 'rb')
        if not submission_file:
            sys.stderr.write(ERR_INVALID_FILE)
            return
        files = {"project_submission[file]": submission_file}
        sys.stdout.write("Submitting...\n")
        submission_request = requests.post(url, files=files, data=data, headers=headers)
        result = json.loads(submission_request.text)
        submission_file.close()
        if "project_submission_id" in result:
            sys.stdout.write("Submission sucessful! Click here for your results: {}/project_"\
                             "submissions/{}\n".format(API_URL, result["project_submission_id"]))
        else:
            sys.stderr.write(ERR_INVALID_CRED)
            continuous_prompt()
            submit(filename, project_id)
    else:
        sys.stderr.write(ERR_INVALID_CRED)
        continuous_prompt()
        submit(filename, project_id)
###HELPER METHODS

class Subcommand(Command):
    """override the command class and override the take_action method"""
    log = logging.getLogger(__name__)
    def take_action(self, parsed_args):
        """override so the subcommand can be called"""
        pass

###COMMANDS
class Version(Subcommand):
    "prints the version number"
    def run(self, parsed_args):
        self.app.stdout.write('mimir cli v{}\n'.format(__version__))

class New(Subcommand):
    "the new command that allows you to create a new object on the mimir platform."
    def get_parser(self, prog_name):
        """overrides the get_parser method to add an object type"""
        choices = ['project', 'lesson', 'announcement', 'test_case', 'course']
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('item_type', choices=choices)
        return parser

    def run(self, parsed_args):
        self.app.stdout.write('you want to make a new {}\n'.format(parsed_args.item_type))

class Submit(Subcommand):
    "use this command to submit projects to the mimir platform"
    def get_parser(self, prog_name):
        """overrides the get_parser method to add an object type"""
        parser = super(Submit, self).get_parser(prog_name)
        parser.add_argument('-p', '--project_id', help='project_id that you wish to submit to')
        parser.add_argument('filename', help='project folder, zip, or source file')
        return parser

    def run(self, parsed_args):
        credentials = read_credentials()
        if "auth_token" not in credentials:
            self.app.stderr.write(ERR_NOT_AUTH)
            continuous_prompt()
        filename = parsed_args.filename
        project_id = ""
        if parsed_args.project_id:
            project_id = parsed_args.project_id
        if not project_id:
            projects = get_projects_list()
            project = prompt_for_project(projects)
            project_id = project["id"]
        submit(filename, project_id)

class Login(Subcommand):
    "use this command to login to the mimir platform"
    def get_parser(self, prog_name):
        """overrides the get_parser method to add an object type"""
        parser = super(Login, self).get_parser(prog_name)
        parser.add_argument('-e', '--email', help='the email for your account')
        parser.add_argument('-p', '--password', help='the password for your account')
        return parser

    def run(self, parsed_args):
        email = ""
        password = ""
        if parsed_args.email:
            email = parsed_args.email
        else:
            email = INPUT_FUNCTION('Email: ')
        if parsed_args.password:
            password = parsed_args.password
        else:
            password = getpass.getpass()
        if email and password:
            success = login(email, password)
            if success:
                self.app.stdout.write(AUTH_SUCCESS)
            else:
                self.app.stderr.write(ERR_INVALID_CRED)
        else:
            self.app.stderr.write(ERR_INVALID_CRED)

class Logout(Subcommand):
    "use this command to logout of the mimir platform"
    def run(self, parsed_args):
        credentials_path = "{}.credentials".format(MIMIR_DIR)
        os.remove(credentials_path)
        self.app.stdout.write("Successfully logged out of Mimir.\n")
###COMMANDS

class CLI(App):
    """Mimir CLI object"""
    log = logging.getLogger(__name__)
    def __init__(self):
        command = CommandManager('mimir.cli')
        super(CLI, self).__init__(
            description='mimir cli application',
            version=__version__,
            command_manager=command,
        )
        commands = {
            'complete': CompleteCommand,
            'version': Version,
            'submit': Submit,
            'login': Login,
            'logout': Logout
        }
        for key, value in commands.items():
            command.add_command(key, value)

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)

def main(argv=sys.argv[1:]):
    """main method, run cli"""
    app = CLI()
    return app.run(argv)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
