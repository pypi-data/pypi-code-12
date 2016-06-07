from __future__ import absolute_import

from arya.build import git
from pbr.packaging import _get_version_from_pkg_metadata


def get_git_version():
    tag = git.tag()
    count = git.count(tag)
    short = git.short()

    if not tag:
        return '0.dev{count}+{short}'.format(count=count, short=short)
    if count == '0':
        return tag
    return '{tag}.dev{count}+{short}'.format(tag=tag, count=count, short=short)


def get_version(package):
    version = _get_version_from_pkg_metadata(package)
    if version:
        return version

    version = get_git_version()
    return version
