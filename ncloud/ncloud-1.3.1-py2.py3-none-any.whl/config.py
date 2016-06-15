# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
"""
Houses configuration options and loading/saving these to disk
"""
from builtins import str
from builtins import oct
from builtins import object
import json
import logging
import os
import requests
import sys
import stat
import configparser
from ncloud.formatting.output import print_error


logger = logging.getLogger()

CMD_NAME = "ncloud"
CFG_FILE = os.path.join(os.path.expanduser("~"), "." + CMD_NAME + "rc")
CFG_DEF_HOST = "https://helium.cloud.nervanasys.com"
CFG_DEF_AUTH_HOST = "https://auth.cloud.nervanasys.com"
CFG_DEF_API_VER = "v1"
CFG_DEF_TENANT = None
CFG_SEC_DEF = "DEFAULT"

PATH = "/api/"
TOKENS = "/tokens/"
DATASETS = "/datasets/"
MODELS = "/models/"
MULTIPART_UPLOADS = "/multipart/"
RESOURCES = "/resources/"
PREDICTIONS = "/predictions/"

UPGRADE_URL = "https://s3-us-west-1.amazonaws.com/nervana-ncloud/latest"

NUM_THREADS = 100


# TODO rename to ConnectParams
#      allow creating with overrides in init (for test)
#      consider remove display of defaults in argparse, to reduce coupling
class Config(object):
    def __init__(self):
        self.conf = self._load_config()

    def get_default_host(self):
        return self.conf.get(CFG_SEC_DEF, "host")

    def set_default_host(self, host):
        self.conf.set(CFG_SEC_DEF, "host", host)

    def get_default_auth_host(self):
        return self.conf.get(CFG_SEC_DEF, "auth_host")

    def set_default_auth_host(self, auth_host):
        self.conf.set(CFG_SEC_DEF, "auth_host", auth_host)

    def get_default_tenant(self):
        return self.conf.get(CFG_SEC_DEF, "tenant")

    def set_default_tenant(self, tenant):
        self.conf.set(CFG_SEC_DEF, "tenant", tenant)

    def get_default_api_ver(self):
        return self.conf.get(CFG_SEC_DEF, "api_ver")

    def set_default_api_ver(self, api_ver):
        self.conf.set(CFG_SEC_DEF, "api_ver", api_ver)

    def get_credentials(self):
        data = {}
        conf = self.conf
        auth_host = self.get_default_auth_host()
        tenant = self.get_default_tenant()
        for item in ["email", "password", "tenant"]:
            if (item == "tenant" and tenant is not None and
                (not conf.has_option(auth_host, item) or
                 conf.get(auth_host, item) != tenant)):
                conf.set(auth_host, item, tenant)
            if not conf.has_option(auth_host, item):
                logger.warning("Can't generate auth token.  "
                               "Missing {0}".format(item))
                logger.warning("Re-run: {0} configure".format(CMD_NAME))
                sys.exit(1)
            data[item] = conf.get(auth_host, item)
        return data

    def token_req(self, data=None):
        if data is None:
            data = self.get_credentials()

        try:
            res = requests.post(self.token_url(), data=data)
            if res.status_code == 201:
                res = json.loads(res.text)
                return res["token"]
            elif not str(res.status_code).startswith('2'):
                print_error(res)
        except requests.exceptions.RequestException as re:
            logger.error(re)
            sys.exit(1)

    def get_token(self, refresh=False, data=None):
        token = None
        conf = self.conf
        auth_host = self.get_default_auth_host()
        tenant = self.get_default_tenant()
        if (conf.has_option(auth_host, "token") and
           conf.has_option(auth_host, "tenant") and
           conf.get(auth_host, "tenant") == tenant):
            token = conf.get(auth_host, "token")

        if refresh or not token:
            token = self.token_req(data)
            conf.set(auth_host, "token", token)
            self._write_config(conf)

        return token

    def api_url(self):
        """
        Helper to return the base API url endpoint
        """
        return self.get_default_host() + PATH + self.get_default_api_ver()

    def token_url(self):
        """
        Helper to return the auth API url endpoint
        """
        return self.api_url() + TOKENS

    def _validate_config(self, conf):
        """
        Helper that ensures config items are in a compliant format.
        Usually comes about when upgrading and an older .ncloudrc
        is present

        Args:
            conf (SafeConfigParser): loaded config values.

        Returns:
            SafeConfigParser: valid, loaded config values.
        """
        # v0 -> v1 changes:
        api_ver = conf.get(CFG_SEC_DEF, "api_ver")
        if api_ver == "v0":
            conf.set(CFG_SEC_DEF, "api_ver", "v1")
        for host_cfg in ["host", "auth_host"]:
            url = conf.get(CFG_SEC_DEF, host_cfg)
            if not url.startswith("http"):
                conf.set(CFG_SEC_DEF, host_cfg, "https://" + url)
        return conf

    def _load_config(self):
        """
        Helper to read and return the contents of the configuration file.
        Certain defaults may be defined and loaded here as well.

        Returns:
            SafeConfigParser: possibly empty configuration object
        """
        conf = configparser.SafeConfigParser({
            "host": CFG_DEF_HOST,
            "auth_host": CFG_DEF_AUTH_HOST,
            "api_ver": CFG_DEF_API_VER,
            "tenant": CFG_DEF_TENANT
        })

        if os.path.isfile(CFG_FILE):
            if oct(os.stat(CFG_FILE)[stat.ST_MODE])[-2:] != "00":
                # group, or other can rw or x config file.  Nag user
                logger.warn("Insecure config file permissions found.  "
                            "Please run: chmod 0600 {}".format(CFG_FILE))
            conf.read([CFG_FILE])

        conf = self._validate_config(conf)
        return conf

    def _write_config(self, conf):
        """
        Writes the config settings to disk.

        Args:
            conf (SafeConfigParser): configuration settings.
        """
        with open(CFG_FILE, "w") as cf:
            conf.write(cf)
        os.chmod(CFG_FILE, 0o600)
