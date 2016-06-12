# -*- coding: utf-8 -*-

import configparser


class PearConfig(object):

	def getConfig(self, conf_path):
		""" set configure """
		conf = configparser.ConfigParser()
		conf.read(conf_path)
		return conf

if __name__ == '__main__':
	conf = PearConfig()
	result = conf.getConfig('sample.ini')
	print (result['default']['samplevalue'])
	print (result['default']['samplestring'])
