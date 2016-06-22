# This file is a part of the AnyBlok / Pyramid / Beaker project
#
#    Copyright (C) 2016 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid import set_callable
from anyblok.config import Configuration


def get_db_name(request):
    dbname = request.session.get('dbname')
    if not dbname:
        dbname = Configuration.get('db_name')

    return dbname


def anyblok_init_config():
    from . import config  # noqa to update configuration

    set_callable(get_db_name)
