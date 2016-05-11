import os
import json
from netrc import netrc
from urlparse import urlparse
import subprocess
import requests
from maintain.creators.base import Creator, ValidationError
from maintain.creators.git import GitCreator


class GitHubCreator(Creator):
    name = 'github'

    def __init__(self, *args, **kwargs):
        super(GitHubCreator, self).__init__(*args, **kwargs)
        self.private = False
        self.organisation = None

    def __str__(self):
        components = []

        if self.private:
            components.append('private')

        if self.organisation:
            components.append('organisation: {}'.format(self.organisation))

        if len(components) > 0:
            return '{} ({})'.format(self.name, ', '.join(components))

        return '{}'.format(self.name)

    @classmethod
    def dependencies(cls):
        return [GitCreator]

    def validate(self):
        github = self.config['github']
        if isinstance(github, dict):
            self.private = bool(self.config['github.private'])
            self.organisation = self.config['organisation'] or self.config['organization']  # Americans

        self.api_root = self.config['github.api'] or 'https://api.github.com/'
        host = urlparse(self.api_root).hostname
        net = netrc()
        if net.authenticators(host) == None:
            raise ValidationError('Improperly configured git, please add access token to `~/.netrc` for {}'.format(host))

    def create(self):
        if self.organisation:
            url = '{}orgs/{}/repos'.format(self.api_root, self.organisation)
        else:
            url = '{}user/repos'.format(self.api_root)

        payload = {
            'name': self.destination,
            'private': self.private,
        }

        response = requests.post(url, data=json.dumps(payload))
        response.raise_for_status()
        clone_url = response.json()['clone_url']
        git_dir = os.path.join(self.destination, '.git')
        subprocess.call(['git', 'remote', 'add', 'origin', clone_url, '--git-dir={}'.format(git_dir)])

