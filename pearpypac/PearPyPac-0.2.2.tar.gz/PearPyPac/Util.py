# -*- coding: utf-8 -*-

import configparser


class PearConfig:
    def getConfig(self, conf_path):
        """ set configure """
        conf = configparser.ConfigParser()
        conf.read(conf_path)
        return conf
