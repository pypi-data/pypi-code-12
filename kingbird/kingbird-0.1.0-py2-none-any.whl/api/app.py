# Copyright (c) 2015 Huawei, Tech. Co,. Ltd.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import pecan

from keystonemiddleware import auth_token
from oslo_config import cfg
from oslo_middleware import request_id
from oslo_service import service

from kingbird.common import exceptions as k_exc
from kingbird.common.i18n import _


def setup_app(*args, **kwargs):
    config = {
        'server': {
            'port': cfg.CONF.bind_port,
            'host': cfg.CONF.bind_host
        },
        'app': {
            'root': 'kingbird.api.controllers.root.RootController',
            'modules': ['kingbird.api'],
            'errors': {
                400: '/error',
                '__force_dict__': True
            }
        }
    }
    pecan_config = pecan.configuration.conf_from_dict(config)

    # app_hooks = [], hook collection will be put here later

    app = pecan.make_app(
        pecan_config.app.root,
        debug=False,
        wrap_app=_wrap_app,
        force_canonical=False,
        hooks=[],
        guess_content_type_from_ext=True
    )

    return app


def _wrap_app(app):
    app = request_id.RequestId(app)

    if cfg.CONF.auth_strategy == 'noauth':
        pass
    elif cfg.CONF.auth_strategy == 'keystone':
        app = auth_token.AuthProtocol(app, {})
    else:
        raise k_exc.InvalidConfigurationOption(
            opt_name='auth_strategy', opt_value=cfg.CONF.auth_strategy)

    return app


_launcher = None


def serve(api_service, conf, workers=1):
    global _launcher
    if _launcher:
        raise RuntimeError(_('serve() can only be called once'))

    _launcher = service.launch(conf, api_service, workers=workers)


def wait():
    _launcher.wait()
