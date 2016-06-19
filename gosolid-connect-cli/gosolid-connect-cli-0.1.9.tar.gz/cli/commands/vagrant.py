import requests
import json
import os
import sys
import cli.configuration
from subprocess import call
from cli.framework.git_core import Git


class Vagrant():
    def __init__(self, prop, user_data, directory):
        self.directory = directory
        if prop is None:
            self.cwd = os.getcwd()
            self.connect_file = os.path.join(self.cwd + '/.connect')
            self.property = self.get_property_from_dir()
        else:
            self.property = prop
            if self.directory is not None:
                self.cwd = os.path.join(os.getcwd() + '/%s' % self.directory)
            else:
                self.cwd = os.path.join(os.getcwd() + '/%s' % self.property)
            self.connect_file = os.path.join(self.cwd + '/.connect')

        self.property_url = configuration.BASE_URL + 'property/%s' % self.property
        self.vagrant_file_url = self.property_url + "/vagrantfile"
        self.vagrant_file = os.path.join(self.cwd + '/%s' % configuration.VAGRANTFILE_NAME)
        self.vagrant_folder = os.path.join(self.cwd + '/.vagrant')
        self.git_folder = os.path.join(self.cwd + '/.git')
        self.user_data = user_data
        self.property_data = None

        self.no_env_error = 'Environment not yet built. Please run "connect init -p %s" to create one.' % self.property

        self.refresh_property_data()

    #Gets latest data about the property from Connect
    def refresh_property_data(self):
        data = requests.get(self.property_url, headers={
            'email': self.user_data['email'],
            'secret-key': self.user_data['secret_key']
        })
        reply = json.loads(data.text)
        if reply['success']:
            self.property_data = reply['result']
            return True
        else:
            print reply['errors'][0]['messages'][0]
            return False

    def get_property_from_dir(self):
        if os.path.exists(self.connect_file):
            with open(self.connect_file, 'r') as f:
                lines = f.readlines()
                if lines[0] == '':
                    return None
                else:
                    return lines[0]
        else:
            print 'FATAL: No property name set. Please include a 4-letter property name (and optional directory) to initialize an environment. For help, run "connect -h".'
            sys.exit()

    def init(self):
        if not os.path.exists(self.vagrant_file):
            name = self.property_data['name']
            print 'Creating development environment for %s...' % name
            if not os.path.exists(self.git_folder):
                Git(self.property_data, self.user_data, self.directory).init_repo()
            #w+ file mode overwrites everything already present in the file
            with open(self.connect_file, 'w+') as f:
                f.seek(0)
                f.write(self.property_data['code'].lower())
                f.flush()
            with open(self.vagrant_file, 'w+') as f:
                f.seek(0)
                remote_vagrant_file = requests.get(self.vagrant_file_url, headers={
                    'email': self.user_data['email'],
                    'secret-key': self.user_data['secret_key']
                })
                f.write(remote_vagrant_file.text)
                f.flush()
            print 'Congratulations! Your %s dev environment is ready! Starting...' %(name, command_to_run)
            self.start()
        else:
            print 'Development environment already exists at this location. Exiting.'
            sys.exit()

    def start(self):
        try:
            os.chdir(self.cwd)
            call(["vagrant", "up"])
        except OSError:
            print self.no_env_error

    def stop(self):
        try:
            os.chdir(self.cwd)
            call(["vagrant", "halt"])
        except OSError:
            print self.no_env_error


    def ssh(self):
        try:
            os.chdir(self.cwd)
            call(["vagrant", "ssh"])
        except OSError:
            print self.no_env_error

    def destroy(self):
        try:
            os.chdir(self.cwd)
            call(["vagrant", "destroy"])
        except OSError:
            print self.no_env_error

    def reset(self):
        self.destroy()
        os.remove(self.vagrant_file)
        os.remove(self.vagrant_folder)
        os.remove(self.git_folder)
        self.refresh_property_data()
        self.init()