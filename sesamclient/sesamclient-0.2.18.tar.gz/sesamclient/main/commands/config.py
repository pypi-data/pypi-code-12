# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import configparser
import os.path

import appdirs

data_dir = appdirs.user_data_dir(appname="sesamclient", appauthor="Sesam")
configfilename = os.path.join(data_dir, "settings.ini")
myconfigparser = configparser.ConfigParser()
myconfigparser.read(configfilename, encoding="utf-8")


def config_cmd(args):
    """This function handles the 'config' command.

    Note that we don't have to check if the args.optionname is valid here, since that check has already been
    performed by the argparser.

    :param args: The arguments to the config-command.
    """
    if "." not in args.optionname:
        raise AssertionError("config key does not contain a section: %s" % (args.optionname,))

    section, optionname = args.optionname.split(".", maxsplit=1)

    if args.optionvalue:
        # set the config value
        optionvalue = " ".join(args.optionvalue)
        if not myconfigparser.has_section(section):
            myconfigparser.add_section(section)
        myconfigparser.set(section, optionname, optionvalue)

        os.makedirs(data_dir, exist_ok=True)
        with open(configfilename, "w", encoding="utf-8") as configfile:
            myconfigparser.write(configfile)
    else:
        # get the configvalue
        value = myconfigparser.get(section, optionname, fallback="")
        if value:
            print(value)
