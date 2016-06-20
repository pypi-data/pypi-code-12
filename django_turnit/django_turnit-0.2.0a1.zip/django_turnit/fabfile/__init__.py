# -*- coding: utf-8 -*-
"""
fabric commands for :app:`django_turnit`

:creationdate: 09/03/16 11:16
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.fabfile

"""
from fabric import api

from . import conf

MODULES= ['django_turnit', ]

@api.task
def sphinx_autogen(modules=MODULES, version='0.1', revision=1):
    """
    Auto-generate docs rst files, based on modules names. Version / revisions can be provided.

    .. note::
        Version is like '1.2', and revision MUST be a single number

    :param modules: list of modules to auto-generate
    :param version: major version number as "0.2"
    :param revision: revision number as single number, as `42`
    :returns: Nothing
    """
    with api.lcd(conf.PROJECT['docs_dir']):
        for module in modules:
            cmd = ('sphinx-apidoc -H intranet -V %(version)s -R %(version)s.%(revision)s '
                   '-P -f -M -o source %(src_dir)s/'
                   % {'version': version,
                      'revision': revision,
                      'src_dir': conf.PROJECT['src_dir'],
                      'module': module})
            api.local(cmd)


@api.task
def sphinx_build():
    """
    Build sphinx docs
    """
    # locally launch `make` commands to build sphinx docs
    with api.lcd(conf.PROJECT['docs_dir']):
        api.local('make clean')
        api.local('make html')


@api.task
def sphinx_svn_commit(display=True):
    """
    Commit documentations and update documentation on ulysse server,
    then open locally generated documentation
    """
    # Commit docs
    with api.lcd(conf.PROJECT['docs_dir']):
        api.local('git add --ignore-errors *')
        api.local('git commit -m "Update documentation !"')
    # Update docs on ulysse
    with api.settings(user='intervention', host_string='ulysse.ville.tg'):
        with api.cd(conf.PROJECT['docs_html']):
            api.run('svn update')
    # Locally browse docs
    # if display:
    #     api.local('xdg-open ' + conf.PROJECT['docs_url'])


@api.task
def sphinx(modules=MODULES, version='0.2', revision='1'):
    """
    Auto-generate, build and commit docs

    .. note:: Version is like '1.2', and revision MUST be a single number

    :param modules: list of modules to auto-generate
    :param version: Major version number as "0.2"
    :param revision: revision number as single number, as "42"
    """
    # Autogen docs
    sphinx_autogen(modules, version, revision)
    # Build docs
    sphinx_build()
    # Commit docs to snv and update remote server
    sphinx_svn_commit()
