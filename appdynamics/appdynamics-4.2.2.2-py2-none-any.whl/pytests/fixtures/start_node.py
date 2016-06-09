from . import config

START_NODE_RESPONSE = {
    'dataSocketDirPath': '/tmp/test1',
}

START_NODE_RESPONSE_WITH_CONFIG = dict(
    START_NODE_RESPONSE,
    configResponse=config.COMPLEX_CONFIG
)
