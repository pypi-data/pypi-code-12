import os
import sys
import argparse
import requests
import base64
from kazoo.client import KazooClient
from dcos import (
    util,
    http
)
from dcos.errors import (
    DCOSHTTPException,
    DCOSAuthorizationException
)

ON_DCOS = True if 'DCOS_SSL_VERIFY' in os.environ else False

BASE_USAGE = """concord [-h] [--info] [--version] subcommand [suboptions [suboptions ...]]"""

POSITIONAL = """
\npositional arguments: (one of)
  deploy\tDeploy concord operators
  kill\t\tLaunch interactive session to browse and kill operators
  graph\t\tCreate a graphical representation of the current topology
  marathon\tCreate a marathon application from given parameters
  config\tSet global CLI defaults
"""

USAGE = BASE_USAGE + POSITIONAL

def dcos_options(parser):
    """Adds dcos specific options to the initial argument parser"""
    if ON_DCOS is not True:
        return
    parser.add_argument('--config-schema', action='store_true', help='Schema Validator')

def dcos_config_data():
    """Fetches config data from dcos schema"""
    config_data = {}
    config_data['zookeeper_hosts'] = util.get_config().get('concord.zookeeper_hosts')
    config_data['zookeeper_path'] = util.get_config().get('concord.zk_path')
    return config_data

def dcos_fetch_credentials():
    """Fetches scheme and credentials if 401 is returned"""
    token = util.get_config().get("core.dcos_acs_token")
    if token is None:
        raise DCOSAuthenticationException("Must authenticate first, try: dcos auth login")
    return ('Basic', base64.b64encode(token))

def get_zookeeper_master_ip(zkurl, zkpath):
    print("Connecting to:%s" % zkurl)
    auth = None
    if ON_DCOS is not True:
        auth = [dcos_fetch_credentials()]
        print auth
    zk = KazooClient(hosts=zkurl, auth_data=auth)
    try:
        zk.start()
    except Exception as e:
        print e
    
    
        
