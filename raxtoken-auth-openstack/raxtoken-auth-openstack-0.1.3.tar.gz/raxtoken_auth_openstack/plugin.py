"""
Auth Extension for Rackspace Public Cloud.

Copyright 2012 Rackspace.
Copyright 2012 Hewlett-Packard Development Company, L.P.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

import novaclient.auth_plugin

from novaclient import exceptions as exc

from novaclient.i18n import _

IDENTITY_US = "https://identity.api.rackspacecloud.com/v2.0/"
IDENTITY_UK = "https://lon.identity.api.rackspacecloud.com/v2.0/"


def determine_auth_url(args):
    """Use Region to determine auth url if none is specified."""
    if args.os_auth_url:
        return args.os_auth_url
    elif args.os_region_name and args.os_region_name.lower() == "lon":
        return IDENTITY_UK
    else:
        return IDENTITY_US


def _authenticate(cls, opts):
    """Authenticate with tenant and token."""
    body = {
        "auth": {
            "tenantId": opts["os_project_id"],
            "token": {
                "id": opts["os_auth_token"]
            }
        }
    }
    return cls._authenticate(opts["os_auth_url"], body)


class RackspaceAuthPlugin(novaclient.auth_plugin.BaseAuthPlugin):
    """Plugin simply provides authenticate, no extra options."""

    def authenticate(self, cls, auth_url):
        """Override Static Method from parent class."""
        _authenticate(cls, self.opts)

    def get_auth_url(self):
        """
        Return default auth_url for the plugin.

        Placeholder function to prevent error when
        --os-auth-url is not set. unless an auth url
        is explicitly set, default auth url will be
        determined in parse_opts().
        """
        return IDENTITY_US

    def parse_opts(self, args):
        """
        Parse Opts from Argparse return.

        Currently the add_opts method appears to be
        Broken, so we rely on the existing parser options.
        """
        # add_opts method appears to be broken as of 5/4/16,
        # shell.py does not pass an instance of RackspaceAuthPlugin
        # as the first argument when called.

        parameters = [
            args.os_project_id,
            args.os_project_name,
            args.os_tenant_name
        ]

        project_id = ""
        for param in parameters:
            if param:
                project_id = param

        if not project_id:
            raise exc.CommandError(_("You must provide a project name or"
                                     " project id via --os-project-name,"
                                     " --os-project-id, env[OS_PROJECT_ID]"
                                     " or env[OS_PROJECT_NAME]. You may"
                                     " use os-project and os-tenant"
                                     " interchangeably."))

        if not args.os_password:
            raise exc.CommandError(_("You must provide an auth token"
                                     " via --os-password or env[OS_PASSWORD]"))
        if not args.os_region_name:
            raise exc.CommandError(_("You must provide a valid region via"
                                     " --os-region-name or"
                                     " env[OS_REGON_NAME]"))

        # Upstream novaclient does not pass --os-token
        # into the args passed to plugins, so we utilize
        # os_password
        self.opts = {
            "os_project_id": project_id,
            "os_auth_token": args.os_password,
            "os_auth_url": determine_auth_url(args)
        }

        return self.opts
