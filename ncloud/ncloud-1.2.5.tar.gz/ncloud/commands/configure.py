# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Configure subcommand.
"""
from builtins import input
import getpass
import logging
from ncloud.commands.command import Command
from ncloud.config import CFG_FILE, CFG_SEC_DEF

logger = logging.getLogger()


class Configure(Command):
    @classmethod
    def parser(cls, subparser):
        config = subparser.add_parser("configure",
                                      help="Update stored configuration "
                                           "options like email, password, "
                                           "and tenant.")
        config.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, host, auth_host, tenant, api_ver):
        """
        Create/update stored configuration credentials.
        Prompts the user for info
        """
        conf = config.conf
        if not conf.has_section(auth_host):
            conf.add_section(auth_host)
        defaults = {key: val for (key, val) in conf.items(auth_host)}
        logger.info("Updating {0} configuration.  Defaults are in "
                    "'[]'".format(CFG_FILE))
        data = {}
        for item in ("email", "password", "tenant"):
            default = defaults.get(item, "")
            if item == "tenant" and default == "" and tenant is not None:
                default = tenant
            if item == "password":
                res = getpass.getpass("{0}: ".format(item))
            else:
                res = input("{0} [{1}]: ".format(item, default))
            if len(res.strip()) == 0 and len(default.strip()) > 0:
                res = default
            conf.set(auth_host, item, res)
            data[item] = res
            if item == "tenant" and default == "":
                # no prior tenant default set, use the one just provided
                conf.set(CFG_SEC_DEF, "tenant", res)

        config.get_token(refresh=True, data=data)
