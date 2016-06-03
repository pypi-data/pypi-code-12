# -*- coding: utf-8 -*-

"""
Recipe celery:

* http://docs.celeryproject.org/en/latest/
* https://github.com/collective/collective.recipe.celery
"""

import os
from mako.template import Template

import zc.buildout
import zc.recipe.egg
from birdhousebuilder.recipe import conda, supervisor
from birdhousebuilder.recipe.conda import as_bool, makedirs

templ_config_py = Template(filename=os.path.join(os.path.dirname(__file__), "celeryconfig_py"))
templ_celery_cmd = Template(
     "${bin_dir}/celery worker -A ${app} --loglevel=${loglevel}")
templ_flower_cmd = Template(
     "${bin_dir}/celery flower -A ${app} --loglevel=${loglevel}")

class Recipe(object):
    """This recipe is used by zc.buildout.
    It installs Celery with conda and setups the configuration."""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        self.options['user'] = options.get('user', '')
        self.options['app'] = options.get('app', 'myapp')
        self.use_monitor = as_bool(self.options.get('use-monitor', 'false'))
        self.use_celeryconfig = as_bool(self.options.get('use-celeryconfig', 'true'))
        self.options['broker-url'] = self.options.get('broker-url', 'redis://localhost:6379/0')
        self.options['celery-result-backend'] = self.options.get('celery-result-backend', 'redis://localhost:6379/0')
        self.options['loglevel'] = self.options.get('loglevel', 'WARNING')
        self.conf_filename = os.path.join(self.prefix, 'etc', 'celery', 'celeryconfig.py')

        self.bin_dir = b_options.get('bin-directory')
        self.options['bin_dir'] = self.bin_dir

    def install(self, update=False):
        installed = []
        installed += list(self.install_conda(update))
        installed += list(self.install_script())
        if self.use_celeryconfig:
            installed += list(self.install_config_py())
        installed += list(self.install_celery_supervisor(update))
        if self.use_monitor:
            installed += list(self.install_flower_supervisor(update))
        return installed

    def install_conda(self, update=False):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'celery flower redis-py'})
        if update == True:
            return script.update()
        else:
            return script.install()

    def install_script(self):
        eggs = ['celery', 'flower', 'redis']
        if 'eggs' in self.options:
            eggs = eggs + self.options['eggs'].split()
        celery_egg_options = {
            'eggs': '\n'.join(eggs),
            'extra-paths': os.path.dirname(self.conf_filename),
            #'entry-points': 'celery=celery.__main__:main',
            'scripts': 'celery=celery'}
       
        celery_egg = zc.recipe.egg.Egg(
            self.buildout,
            self.name,
            celery_egg_options,
        )
        return list(celery_egg.install())
        
    def install_config_py(self):
        result = templ_config_py.render(options=self.options)
        output = self.conf_filename
        makedirs(os.path.dirname(output))

        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_celery_supervisor(self, update=False):
        """
        install supervisor config for celery
        """
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'user': self.options.get('user'),
             'program': self.name,
             'command': templ_celery_cmd.render(**self.options),
             'stopwaitsecs': '30',
             'killasgroup': 'true',
             })
        return script.install(update)

    def install_flower_supervisor(self, update=False):
        """
        install supervisor config for flower
        """
        script = supervisor.Recipe(
            self.buildout,
            self.name,
            {'user': self.options['user'],
             'program': self.name + '_monitor',
             'command': templ_flower_cmd.render(**self.options),
             'stopwaitsecs': '30',
             'killasgroup': 'true',
             })
        return script.install(update)
    
    def update(self):
       return self.install(update=True)

def uninstall(name, options):
    pass

