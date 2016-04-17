import glob
import logging
import os
import re
import shutil
import itertools
import zc.buildout
from hexagonit.recipe import cmmi


class Recipe(object):
    """Receta para instalar redis."""

    no_conf_options = ['location', 'url', 'recipe']

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.url = options['url']
        
        if options.has_key('location'):
            options['location'] = os.path.join(
                buildout['buildout']['directory'], options['location']
            )
        else:
            options['location'] = os.path.join(buildout['buildout']['parts-directory'], name)
            
        if os.path.exists(options['location']) and not os.path.isdir(options['location']):
            logging.getLogger(self.name).error(
                '%s existe pero no es un directorio.',
                options['location'], os.path.dirname(options['location'])
            )

            raise zc.buildout.UserError('Directorio invalido.')

    def _get_configutation(self, conf_file):
        conf = open(conf_file).read()

        conf_options = [(k, self.options[k])
                        for k in set(self.options) - set(self.no_conf_options)]

        for co, co_value in conf_options:
            regex_str = '^(#\s)?%s\s\w.*\n' % co
            regex = re.compile(regex_str, re.MULTILINE)

            if not len(re.findall(regex, conf)) == 1:
                raise zc.buildout.UserError(
                    "La expresion regular %r no se encontro o se encontro "
                    "mas de una vezen redis.conf" % regex_str)

            conf = re.sub(regex,"%s %s\n" % (co, co_value), conf)

        return conf

    def install(self):
        location = self.options['location']
        if os.path.exists(location): shutil.rmtree(location)
        
        cmmi_options = {
            'configure-command': 'echo No configure',
            'keep-compile-dir': 'true',
            'make-options': 'PREFIX=%s' % location,
            'url': self.url
        }

        rcp = cmmi.Recipe(self.buildout, self.name, cmmi_options)

        try:
            rcp.install()
            old_conf_file = glob.glob(
                rcp.options['compile-directory'] + '/*/*.conf')[0]

            conf = self._get_configutation(old_conf_file)
            new_conf_file = "%s/redis.conf" % location
            open(new_conf_file, "w").write(conf)

            return [new_conf_file] + glob.glob(location + '/bin/*')
        finally:
            if os.path.exists(rcp.options['compile-directory']):
                shutil.rmtree(rcp.options['compile-directory'])


    def update(self):
        pass