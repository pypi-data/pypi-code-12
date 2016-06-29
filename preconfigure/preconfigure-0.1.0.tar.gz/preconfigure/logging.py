import os
import yaml
import logging
import logging.config

path = os.getenv("LOGGING_CONF")

if path:
	with open(path, 'r') as f:
		config = yaml.load(f)
	logging.config.dictConfig(config)
else:
	logging.basicConfig(level = logging.INFO)

if __name__ == "__main__":
	from . import _chain
