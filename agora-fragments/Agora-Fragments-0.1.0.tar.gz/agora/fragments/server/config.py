"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""

import logging

import os

__author__ = 'Fernando Serena'


def _api_port():
    return int(os.environ.get('API_PORT', 5006))


def _stoa_conf(def_broker_host, def_broker_port, def_agora_host, def_agora_port, def_exchange,
               def_topic_pattern, def_response_prefix):
    return {
        'broker_host': os.environ.get('BROKER_HOST', def_broker_host),
        'broker_port': int(os.environ.get('BROKER_PORT', def_broker_port)),
        'agora_host': os.environ.get('AGORA_HOST', def_agora_host),
        'agora_port': int(os.environ.get('AGORA_PORT', def_agora_port)),
        'exchange': os.environ.get('EXCHANGE_NAME', def_exchange),
        'topic_pattern': os.environ.get('TOPIC_PATTERN', def_topic_pattern),
        'response_prefix': os.environ.get('RESPONSE_PREFIX', def_response_prefix)
    }


class Config(object):
    PORT = 5006
    STOA = _stoa_conf('localhost', 5672, 'localhost', 9009, 'stoa', 'stoa.request', 'stoa.response')


class DevelopmentConfig(Config):
    DEBUG = True
    LOG = logging.DEBUG


class TestingConfig(Config):
    DEBUG = False
    LOG = logging.DEBUG
    TESTING = True
    STORE = 'memory'


class ProductionConfig(Config):
    DEBUG = False
    LOG = logging.INFO
