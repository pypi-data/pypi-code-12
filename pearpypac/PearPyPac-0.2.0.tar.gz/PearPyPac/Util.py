# -*- coding: utf-8 -*-

import ConfigParser


class PearConfig:
    def getConfig(self, conf_path):
        """ set configure """
        conf = ConfigParser.SafeConfigParser()
        conf.read(conf_path)
        return conf
