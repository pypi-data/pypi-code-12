from __future__ import absolute_import

from arya.build import git


def get_version():
    tag = git.tag()
    count = git.count(tag)
    short = git.short()

    if not tag:
        return '0.dev{count}+{short}'.format(count=count, short=short)
    if count == '0':
        return tag
    return '{tag}.dev{count}+{short}'.format(tag=tag, count=count, short=short)
