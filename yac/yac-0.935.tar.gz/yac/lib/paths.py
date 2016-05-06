import os

def get_config_path():

	config_path = os.path.join(os.path.dirname(__file__),'../','config')

	return config_path

def get_root_path():

	root_path = os.path.join(os.path.dirname(__file__),'../')

	return root_path

def get_yac_path():

	yac_path = os.path.join(os.path.dirname(__file__),'../../')

	return yac_path

def get_lib_path():

	lib_path = os.path.join(os.path.dirname(__file__))

	return lib_path	