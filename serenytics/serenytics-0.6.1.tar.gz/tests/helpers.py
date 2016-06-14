import logging
import os
import os.path as osp

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def load_env_file():
    """
    Try to update environment variables with the config stored in your '.env' file.
    Useful for customizing dev options.
    """
    config = {}
    try:
        this_directory = osp.dirname(osp.realpath(__file__))
        env_file = osp.join(this_directory, '..', '.env')
        with open(env_file) as env_file:
            for line in env_file:
                splits = line.strip().split('=')
                config[splits[0]] = '='.join(splits[1:])
    except:
        logger.info("could not load config from .env file")

    os.environ.update(config)
