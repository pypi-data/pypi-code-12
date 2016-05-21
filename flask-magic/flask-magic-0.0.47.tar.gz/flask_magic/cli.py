"""
________________________________________________________________________________

flask

 /$$      /$$  /$$$$$$   /$$$$$$  /$$$$$$  /$$$$$$
| $$$    /$$$ /$$__  $$ /$$__  $$|_  $$_/ /$$__  $$
| $$$$  /$$$$| $$  \ $$| $$  \__/  | $$  | $$  \__/
| $$ $$/$$ $$| $$$$$$$$| $$ /$$$$  | $$  | $$
| $$  $$$| $$| $$__  $$| $$|_  $$  | $$  | $$
| $$\  $ | $$| $$  | $$| $$  \ $$  | $$  | $$    $$
| $$ \/  | $$| $$  | $$|  $$$$$$/ /$$$$$$|  $$$$$$/
|__/     |__/|__/  |__/ \______/ |______/ \______/

"""

import os
import re
import sys
import traceback
import logging
import importlib
import pkg_resources
import utils
import click
import yaml
import functools
import sh
from __about__ import *

CWD = os.getcwd()
SKELETON_DIR = "app-skel"
APPLICATION_DIR = "%s/application" % CWD
APPLICATION_DATA_DIR = "%s/_data" % APPLICATION_DIR


def get_project_dir_path(project_name):
    return "%s/%s" % (APPLICATION_DIR, project_name)


def copy_resource(src, dest):
    """
    To copy package data to destination
    """
    dest = (dest + "/" + os.path.basename(src)).rstrip("/")
    if pkg_resources.resource_isdir("flask_magic", src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for res in pkg_resources.resource_listdir(__name__, src):
            copy_resource(src + "/" + res, dest)
    else:
        if not os.path.isfile(dest) \
                and os.path.splitext(src)[1] not in [".pyc"]:
            with open(dest, "wb") as f:
                f.write(pkg_resources.resource_string(__name__, src))
        else:
            print("File exists: %s " % dest)


def create_project(project_name, skel="basic"):
    """
    Create the project
    """
    project_dir = get_project_dir_path(project_name)
    app_tpl = pkg_resources.resource_string(__name__, '%s/app.py' % (SKELETON_DIR))
    propel_tpl = pkg_resources.resource_string(__name__, '%s/propel.yml' % (SKELETON_DIR))
    config_tpl = pkg_resources.resource_string(__name__, '%s/config.py' % (SKELETON_DIR))
    model_tpl = pkg_resources.resource_string(__name__, '%s/model.py' % (SKELETON_DIR))
    manage_tpl = pkg_resources.resource_string(__name__, '%s/magic.py' % (SKELETON_DIR))
    gitignore_tpl = pkg_resources.resource_string(__name__, '%s/gitignore' % (SKELETON_DIR))

    app_file = "%s/app_%s.py" % (CWD, project_name)
    requirements_txt = "%s/requirements.txt" % CWD
    propel_yml = "%s/propel.yml" % CWD
    config_py = "%s/config.py" % APPLICATION_DIR
    model_py = "%s/model.py" % APPLICATION_DIR
    manage_py = "%s/magic.py" % CWD
    gitignore = "%s/.gitignore" % CWD

    dirs = [
        APPLICATION_DIR,
        APPLICATION_DATA_DIR,
        project_dir
    ]
    for d in dirs:
        if not os.path.isdir(d):
            os.makedirs(d)

    files = [
        ("%s/__init__.py" % APPLICATION_DIR, "# Flask-Magic"),
        (config_py, config_tpl),
        (model_py, model_tpl),
        (app_file, app_tpl.format(project_name=project_name)),
        (requirements_txt, "%s==%s" % (__title__, __version__)),
        (propel_yml, propel_tpl.format(project_name=project_name)),
        (manage_py, manage_tpl),
        (gitignore, gitignore_tpl)
    ]
    for f in files:
        if not os.path.isfile(f[0]):
            with open(f[0], "wb") as f0:
                f0.write(f[1])

    copy_resource("%s/skel/%s/" % (SKELETON_DIR, skel), project_dir)
    copy_resource("%s/%s/" % (SKELETON_DIR, "_data"), APPLICATION_DATA_DIR)

# ------------------------------------------------------------------------------


def propel_deploy_config(cwd, file="propel.yml"):
    with open("%s/%s" % (cwd, file)) as f:
        config = yaml.load(f)["deploy"]
    return config 


def get_deploy_hosts_list(cwd, key=None, file="propel.yml"):
    """
    Returns the remote hosts in propel
    :param cwd:
    :param key:
    :param file:
    :return: list
    """
    config = propel_deploy_config(cwd=cwd, file=file)["hosts"]
    return config[key] if key else [v for k, l in config.items() for v in l]


def get_deploy_assets2s3_list(cwd, file="propel.yml"):
    """
    Return the list of all the assets2s3 repo to publish when deploying
    :param cwd:
    :param file:
    :return: list
    """
    conf = propel_deploy_config(cwd=cwd, file=file)
    return conf["assets2s3"] if "assets2s3" in conf else []


def git_push_to_master(cwd, hosts, name="all", force=False, verbose=True):
    """
    To push to master
    :param cwd:
    :param hosts:
    :param force:
    :return:
    """

    def process_output(line):
        if verbose:
            print(line)

    with sh.pushd(cwd):
        name = "magic_deploy_%s" % name

        if sh.git("status", "--porcelain").strip():
            raise Exception("Repository is UNCLEAN. Commit your changes")

        remote_list = sh.git("remote").strip().split()
        if name in remote_list:
            sh.git("remote", "remove", name)
        sh.git("remote", "add", name, hosts[0])
        if len(hosts) > 1:
            for h in hosts:
                sh.git("remote", "set-url", name, "--push", "--add", h)
            _o = ["push", name, "master"]
            if force:
                _o.append("--force")
            sh.git(*_o, _out=process_output)
            sh.git("remote", "remove", name)


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
def catch_exception(func):
    @functools.wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            print("-" * 80)
            print("Exception Uncaught")
            print("-" * 80)
            print(ex)
            print("-" * 80)

    return decorated_view


def cwd_to_sys_path():
    sys.path.append(CWD)


def import_module(project, is_app=False):
    cwd_to_sys_path()
    project = project_name("app_" + project if is_app else project)
    return importlib.import_module(project)


def project_name(name):
    return re.compile('[^a-zA-Z0-9_]').sub("", name)


def header(title=None):
    print(__doc__)
    print("v. %s" % __version__)
    print("_" * 80)
    if title:
        print("** %s **" % title)


def build_assets(mod):
    from webassets.script import CommandLineEnvironment

    module = import_module(mod, True)
    assets_env = module.app.jinja_env.assets_environment

    log = logging.getLogger('webassets')
    log.addHandler(logging.StreamHandler())
    log.setLevel(logging.DEBUG)

    cmdenv = CommandLineEnvironment(assets_env, log)
    cmdenv.build()

def _assets2s3(project):

    import flask_s3
    module = import_module(project, True)

    header("Building assets files for project: %s ..." % project)
    print("")
    build_assets(project)

    print("Uploading assets files to S3 ...")
    flask_s3.create_all(module.app)
    print("")

@click.group()
def cli(): pass


@cli.command("create")
@click.argument("project")
@click.option("--skel", "-s", default="app")
@catch_exception
def new(project, skel):
    """  Create a new Project in the current directory """

    app = project_name(project)

    header("Create New Project ...")
    print("- Project: %s " % app)

    create_project(app, skel)
    print("")
    print("----- That was Magic! ----")
    print("")
    print("- Your new project [ %s ] has been created" % app)
    print("- Location: [ application/%s ]" % app)
    print("")
    print("> What's next?")
    print("- Edit the config [ application/config.py ] ")
    print("- If necessary edit and run the command [ magic setup ]")
    print("- Launch app on devlopment mode, run [ magic serve %s ]" % app)
    print("")
    print("*" * 80)


@cli.command("build-assets")
@click.argument("project")
@catch_exception
def buildassets(project):
    """ Build web assets files """

    header("Build project's assets files from bundles: %s ..." % project)
    print("")
    build_assets(project)
    print("Done!")

@cli.command("assets-to-s3")
@click.argument("project")
@catch_exception
def assets2s3(project):
    """ To upload assets files to S3"""
    _assets2s3(project)


@cli.command("serve")
@click.argument("project")
@click.option("--port", "-p", default=5000)
@click.option("--no-watch", is_flag=True)
@catch_exception
def serve(project, port, no_watch):
    """ Serve application in development mode """

    header("Serving application in development mode ... ")
    print("- Project: %s " % project)
    print("")
    print("- Port: %s" % port)
    print("")

    module = import_module(project, True)

    extra_files = []
    if not no_watch:
        extra_dirs = [CWD,]
        extra_files = extra_dirs[:]
        for extra_dir in extra_dirs:
            for dirname, dirs, files in os.walk(extra_dir):
                for filename in files:
                    filename = os.path.join(dirname, filename)
                    if os.path.isfile(filename):
                        extra_files.append(filename)

    module.app.run(debug=True,
                   host='0.0.0.0',
                   port=port,
                   extra_files=extra_files)


@cli.command("deploy")
@click.option("--remote", "-r", default=None)
@click.option("--assets-to-s3", "-a", is_flag=True)
@click.option("--verbose", "-v", is_flag=True, default=False)
@click.option("--force", "-f", is_flag=True, default=False)
@catch_exception
def deploy(remote, assets_to_s3, verbose, force):
    """ To DEPLOY your application """

    header("Deploying...")

    if assets_to_s3:
        for mod in get_deploy_assets2s3_list(CWD):
            _assets2s3(mod)

    remote_name = remote or "ALL"
    print("Pushing application's content to remote: %s " % remote_name)
    hosts = get_deploy_hosts_list(CWD, remote or None)
    git_push_to_master(cwd=CWD, hosts=hosts, name=remote_name, verbose=verbose, force=force)
    print("Done!")

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------

def cmd():
    """
    Help to run the command line
    :return:
    """
    if os.path.isfile(os.path.join(os.path.join(CWD, "magic.py"))):
        import_module("magic")
    else:
        print("-" * 80)
        print("** Missing << 'magic.py' >> @ %s" % CWD)
        print("-" * 80)
    cli()


