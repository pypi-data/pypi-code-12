import sys

from cratis.generators.module import SettingsModuleFile
from cratis.generators.requirements import add_to_requirements
from pkg_resources import load_entry_point, iter_entry_points

import re

from collections import namedtuple
from cratis.bootstrap import run_env_command


Url = namedtuple('Url', ['feature', 'user', 'version', 'repo', 'protocol'])


# ssh://admin.@django-cratis/cratis-admin#master

def parse_repo_parts(url):

    rx = '^((?P<protocol>[\w-]+):)?(?P<feature>[\w-]+)(?P<exact_feature>\.)?(@(?P<user>[\w-]+))?(/(?P<repo>[\w-]+))?(#(?P<version>[\w-]+))?'

    m = re.match(rx, url)

    feature = m.group('feature')
    exact_feature = m.group('exact_feature')
    if not exact_feature:
        feature = 'cratis-%s' % feature

    user = m.group('user') or 'django-cratis'
    version = m.group('version') or 'master'
    repo = m.group('repo') or feature
    protocol = m.group('protocol') or 'https'
    protocol = 'git+%s' % protocol

    return Url(
        feature=feature,
        user=user,
        version=version,
        repo=repo,
        protocol=protocol
    )


def compile_url(url: Url):
    return '%(protocol)s://github.com/%(user)s/%(repo)s.git@%(version)s#egg=%(feature)s' % url._asdict()


def add_cmd(url, **kwargs):
    data = parse_repo_parts(url)
    url = compile_url(data)

    requirement_url = '-e %s' % url
    run_env_command('pip install %s' % requirement_url)
    run_env_command('cratis-add %s' % data.feature)

    add_to_requirements(data.feature, requirement_url)


def add_feature_to_settings():

    if len(sys.argv) < 2:
        print("Not enough arguments - exit")

    print('\nAdding feature to settings: %s' % sys.argv[1])

    found = []
    for entry_point in iter_entry_points(group='features', name=sys.argv[1]):
        found.append(entry_point.load())

    if not found:
        print("Feature not found")
        sys.exit(1)

    cls = found[0]

    f = SettingsModuleFile('settings')
    f.add_feature(cls.__module__, cls.__name__, getattr(cls, "DEFAULT"))
    f.save()
