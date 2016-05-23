import requests

TIMEOUT = 10
CONTENT_FETCHER_SLEEP = 5
DEFAULT_LENGTH = 30
INCLUDE_SOURCE = False
TWITTER_STREAM_GET_INTERVAL = 50  # Every n tweets
HUB = 'http://pubsubhubbub.appspot.com/'
TWITTER_TITLE_LENGTH = 80
COMMANDS = {
    'daemon': 'resyndicator.daemon.run',
    'random_urn': 'resyndicator.utils.random_urn',
    'shell': 'resyndicator.utils.ipython',
    'server': 'resyndicator.server.run',
}
USER_AGENT = 'python-requests/' + requests.__version__
WEBROOT = 'webroot/'
DATABASE = None
BASE_URL = None
