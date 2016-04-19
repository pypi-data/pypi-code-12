# -*- coding: utf-8 -*-

"""osxstrap.osxstrap: provides entry point main()."""


__version__ = "0.0.32"


import os

import click

import shutil

import common

import output

import ansible

import base64

from shutil import copyfile

from github3 import authorize,login

base_path = os.path.dirname(__file__)

install_path = os.path.realpath(os.path.join(base_path, 'ansible'))

config_path = os.path.join(os.path.expanduser("~"), '.osxstrap')

config_filename = 'config.yml'


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--playbook', '-p', default='playbook', help='Playbook to run.')
@click.option('--ask-sudo-pass', '-k', default=False, is_flag=True, help='Have Ansible prompt you for a sudo password.')
@click.option('--ask-vault-pass', '-v', default=False, is_flag=True, help='Have Ansible prompt you for a vault password.')
def cli(ctx, playbook, ask_sudo_pass, ask_vault_pass):
    common.get_dotenv()
    if ctx.invoked_subcommand is None:  
        ansible.playbook(install_path, playbook, ask_sudo_pass, ask_vault_pass)


@cli.command()
def update():
    common.run('sudo pip install osxstrap -U')
    ansible.galaxy_install(install_path)


@cli.command()
@click.option('-c', '--config-file', default=None, required=True, help='Path of downloaded config file to copy into place.')
def init(config_file):
    copy_config(config_file)
    ansible.galaxy_install(install_path)
    ansible.playbook(install_path, 'playbook', True, False)


def copy_config(source_path):
    if not os.path.isabs(source_path):
        source_path = os.path.join(os.getcwd(), source_path)
    destination_path = os.path.join(config_path, config_filename)
    if source_path and source_path != destination_path:
        if os.path.exists(source_path):
            if not os.path.exists(destination_path):
                common.mkdir(config_path)
                copyfile(source_path, destination_path)
            else:
                output.warning("Destination file %s already exists." % destination_path)
                if click.confirm('Do you want to overwrite it?'):
                    os.remove(destination_path)
                    copyfile(source_path, destination_path)
                else:
                    output.abort("To run osxstrap without copying config, use the osxstrap command.")
        else:
            output.abort("Input file %s does not exist." % source_path)


@cli.command()
@click.option('-e', '--editor', default='webapp', required=False, help='Name of the program to use to edit osxstrap config (i.e. vim). Defaults to opening in the osxstrap webapp.')
def edit(editor):
    if editor == 'webapp':
        config_file_path = os.path.join(config_path, config_filename)
        if os.path.exists(config_file_path):
            f = open(config_file_path)
            config_string = f.read()
            f.close()
            encoded_config_string = base64.b64encode(config_string)
            print encoded_config_string
            common.run('open https://osxstrap.github.io#%s' % encoded_config_string)
        else:
            output.abort("%s does not exist." % config_file_path)
    else:
        common.run('%s %s' % (editor, os.path.join(config_path, config_filename)))


def get_gh_api():
    if not os.environ.get("OSXSTRAP_GITHUB_USERNAME"):
        username = click.prompt('Please enter your Github username')
        common.set_dotenv_key("OSXSTRAP_GITHUB_USERNAME", username)
    else:
        username = os.environ.get("OSXSTRAP_GITHUB_USERNAME")

    if not os.environ.get("OSXSTRAP_GITHUB_API_TOKEN"):
        token = click.prompt('Please create a Github access token by going to https://github.com/settings/tokens/new?scopes=gist&description=osxstrap+gist+cli and enter it here')
        common.set_dotenv_key("OSXSTRAP_GITHUB_API_TOKEN", token)
    else:
        token = os.environ.get("OSXSTRAP_GITHUB_API_TOKEN")
    
    gh = login(token=token)
    return gh

    files = {
    config_filename : {
        'content': 'What... is the air-speed velocity of an unladen swallow?'
        }
    }
    gist = gh.create_gist('Answer this to cross the bridge', files, public=False)
    # gist == <Gist [gist-id]>
    print(gist.html_url)
    system_username = common.run('whoami', capture=True)
    

@cli.command()
def push():
    if not os.environ.get("OSXSTRAP_GITHUB_GIST_ID"):
        if click.confirm("Do you want to set up a Github gist for remote tracking of your osxstrap config file?"):
            get_gh_api()
    else:
    	get_gh_api()
    if os.environ.get("OSXSTRAP_GITHUB_GIST_ID"):
        ghGist = simplegist.Simplegist(username=os.environ.get("OSXSTRAP_GITHUB_USERNAME"), api_token=os.environ.get("OSXSTRAP_GITHUB_API_TOKEN"))
        if os.path.exists(config_file_path):
            f = open(config_file_path)
            config_string = f.read()
            f.close()
            ghGist.profile().edit(id=os.environ.get("OSXSTRAP_GITHUB_GIST_ID"),content=config_string)
