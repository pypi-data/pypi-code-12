# -*- coding: utf-8 -*-

"""osxstrap.ansible: Ansible management for osxstrap."""

import os

import click

import output

import common

config_path = os.path.join(os.path.expanduser("~"), '.osxstrap')

custom_requirements_path = os.path.join(config_path, 'requirements.yml')

custom_roles_path = os.path.join(config_path, 'roles')

custom_playbooks_path = os.path.join(config_path, 'playbooks')

def galaxy_install(install_path):
	roles_path = os.path.join(install_path, 'roles')
	common.mkdir(roles_path)
	common.run('ansible-galaxy install -f -r "%s" -p "%s"' % (os.path.join(install_path, 'requirements.yml'), common.roles_path))
	if os.path.exists(custom_requirements_path):
		if not os.path.exists(custom_roles_path):
			common.mkdir(custom_roles_path)
		common.run('ansible-galaxy install -f -r "%s" -p "%s"' % (custom_requirements_path, custom_roles_path))


def playbook(install_path, playbook='playbook', ask_sudo_pass=False, ask_vault_pass=False, extras=None):
	common.get_dotenv()
	check_roles_dir(install_path)
	os.environ["ANSIBLE_CONFIG"] = os.path.join(install_path, 'ansible.cfg')
	command_string = 'ansible-playbook'
	command_string += ' -i "%s"' % os.path.join(install_path, 'inventory')
	
	if ask_sudo_pass or os.environ.get("OSXSTRAP_ASK_SUDO_PASS") == '1':
		command_string += ' --ask-sudo-pass'
	if ask_vault_pass or os.environ.get("OSXSTRAP_ASK_VAULT_PASS") == '1':
		command_string += ' --ask-vault-pass'
	if extras:
		command_string += ' ' + extras

	default_playbook_path = os.path.join(install_path, playbook) + '.yml'
	if os.path.exists(default_playbook_path):
		command_string += ' "%s"' % default_playbook_path
	else:
		custom_playbook_path = os.path.join(custom_playbooks_path, playbook) + '.yml'
		if os.path.exists(custom_playbook_path):
			command_string += ' "%s"' % custom_playbook_path
		else:
			output.abort("Cannot find playbook %s.yml, looked for it at\n%s\n%s" % (playbook, default_playbook_path, custom_playbook_path))
	common.run(command_string)


def check_roles_dir(install_path):
	if not os.path.exists(common.roles_path):
		output.warning("Roles directory %s does not exist. It is possible that osxstrap init was never run." % common.roles_path)
		if click.confirm('Do you want to run it now?'):
			galaxy_install(install_path)
