import json, logging
from bottle import Bottle, run
import api

def file_get_contents(filename):
	with file(filename) as f:
		s = f.read()

	# Return and remove <FEFF> characters
	return s.replace('\xef\xbb\xbf', '')

def run(port=8080, env='Development'):
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)

	consoleHandler = logging.StreamHandler()
	formatter = logging.Formatter('%(asctime)s - ' + __name__ + ' - %(levelname)s - %(funcName)s - %(message)s')
	consoleHandler.setFormatter(formatter)
	logger.addHandler(consoleHandler)

	cfg = {}
	cfg['env'] = env
	cfg['project'] = '.'
	cfg['debug'] = True

	logger.info("Environment: %s" % cfg['env'])
	logger.info("Service app path: %s" % cfg['project'])

	child_app = Bottle()
	child_app.cfg = cfg

	ms = api.Microservice(child_app)

	appsettingsjson = "%s/appsettings.json" % cfg['project']
	with open(appsettingsjson) as json_data:
		d = json.load(json_data)
		url = d['Service']['UrlPrefix']
		service_name = d['Service']['Name']

	logger.info("Service %s will respond to URL %s" % (service_name, url))

	parent_app = Bottle()
	parent_app.mount(url, child_app)
	logger.info("Mounted child application to %s" % url)
	parent_app.run(host="0.0.0.0", port=8080)

