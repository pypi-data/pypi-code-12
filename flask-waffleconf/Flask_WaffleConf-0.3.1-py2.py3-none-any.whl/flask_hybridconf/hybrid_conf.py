# -*- coding: utf-8 -*-
#
# Flask-HybridConf - https://github.com/rmed/flask-hybridconf
#
# Copyright (C) 2015  Rafael Medina García <rafamedgar@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import json


class HybridConf(object):
    """ Initialize the Flask-HybridConf extension

        Params:

            app         -- Flask application instance
            configstore -- HybridStore instance
            model       -- Model that stores the variables in database
    """

    def __init__(self, app=None, configstore=None, model=None):
        self.app = app
        self.configstore = configstore
        self.model = model

        if app and configstore and model:
            self.init_app(app, configstore)

    def init_app(self, app, configstore):
        """ Initialize the extension for the given application and store.

            Params:

                app         -- Flask application instance
                configstore -- HybridConfStore instance

            Parse the configuration values stored in the database obtained from
            the HYBRID_CONFS value of the configuration.
        """
        configs = app.config.get('HYBRID_CONFS', None)

        if not configs:
            return None

        parsed = self.parse_conf(configs)

        # Update app config
        self.app.config.update(parsed)

    def parse_conf(self, configs):
        """ Parse configuration values from the database specified in the
            *configs* argument. The extension must have been previously
            initialized!

            Params:

                configs -- list of configuration variables (dicts)

                The dicts have the following structure:

                    {
                        'key'     : 'MY_CONFIG_VAR',
                        'type'    : <TYPE OF THE VAR>,
                        'desc'    : <TEXT DESCRIPTION OF THE VAR>,
                        'default' : <DEFAULT VALUE>
                    }

            If a key is not found in the database, itwill be created with the
            default value specified.

            Returns:

                result -- dict of the parsed config values
        """
        result = {}

        for conf in configs:
            db_conf = self.configstore.get(self.model, conf['key'])

            if not db_conf:
                # Create variable in database
                new_var = self.model(key=conf['key'], value=conf['default'])
                db_conf = self.configstore.put(new_var)

            result[db_conf.get_key()] = self.parse_type(conf['type'], db_conf.get_val())

        return result

    def parse_type(self, ctype, config):
        """ Parse the configuration according to the type specified.

            Params:

                ctype  -- type to parse
                config -- configuration value obtained from the database

            Returns:

                parsed -- parsed result
        """
        if ctype == 'str':
            # Default type
            return config

        elif ctype == 'json':
            return json.loads(config)


    def update_conf(self, configs):
        """ Update configuration variables in the database. This also updates
            the application configuration.

            Params:

                configs -- dict configuration variables

                The dicts have the following structure:

                    {
                        'MY_CONFIG_VAR'  : 'CONFIG_VAL',
                        'MY_CONFIG_VAR1' : 'CONFIG_VAL1'
                    }

        """
        result = {}

        try:
            # Python 2.7.x
            iterator = configs.viewitems()

        except:
            # Python 3.x
            iterator = configs.items()

        for key, value in iterator:
            updated = self.model(key=key, value=value)
            self.configstore.put(updated)

            result[key] = value

        self.app.config.update(result)
