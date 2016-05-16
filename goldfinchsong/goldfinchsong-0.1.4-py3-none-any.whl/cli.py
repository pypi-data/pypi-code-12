"""
Command line interface module.

The default logging configuration includes a ``StreamHandler`` and ``RotatingFileHandler``.

Attributes:
    LOGGER_CONFIG (dict): Logging configuration settings. Includes formatters, handlers, loggers
"""
from collections import OrderedDict
import configparser
from logging import config as log_config
from logging import getLogger
import click
from tinydb import TinyDB
from .classes import Manager

logger = getLogger(__name__)

LOGGER_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': 'goldfinchsong.log',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'goldfinchsong': {
            'handlers': ['file', 'console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}


def get_image_directory(command_line_input, active_configuration):
    """
    Provides path to image directory.

    Arguments:
        command_line_input (str | ``None``): A path that may optionally be submitted by user. A string
            or ``None`` are expected types.
        active_configuration (dict): Active configuration options.

    Returns:
        str: A path to the image directory. Default: ``images``
    """
    if command_line_input is not None:
        return command_line_input
    elif 'image_directory' in active_configuration:
        return active_configuration['image_directory']
    return 'images'


def parse_configuration(config_parser):
    """
    Extracts credential and text conversion information.

    Args:
        config_parser: A ``ConfigParser`` from the standard library
            loaded with local configuration file.

    Returns:
        dict: The returned dict contains twitter credentials, any text conversions, and
            any image and/or log configuration information made available.
    """
    active_configuration = dict()
    active_configuration['credentials'] = config_parser['goldfinchsong']
    if config_parser.has_section('goldfinchsong.log'):
        if 'log_level' in config_parser['goldfinchsong.log']:
            active_configuration['log_level'] = config_parser['goldfinchsong.log']['log_level']
            LOGGER_CONFIG['loggers']['goldfinchsong']['level'] = active_configuration['log_level']
        if 'log_location' in config_parser['goldfinchsong.log']:
            active_configuration['log_location'] = config_parser['goldfinchsong.log']['log_location']
            LOGGER_CONFIG['handlers']['file']['filename'] = active_configuration['log_location']
    log_config.dictConfig(LOGGER_CONFIG)
    active_configuration['text_conversions'] = None
    if config_parser.has_section('goldfinchsong.conversions'):
        pairings = config_parser['goldfinchsong.conversions']
        text_conversions = OrderedDict()
        for abbreviated, original in pairings.items():
            text_conversions[original] = abbreviated
        active_configuration['text_conversions'] = text_conversions
    if config_parser.has_section('goldfinchsong.images'):
        images_configuration = config_parser['goldfinchsong.images']
        if 'image_directory' in images_configuration:
            active_configuration['image_directory'] = images_configuration['image_directory']
    if config_parser.has_section('goldfinchsong.db'):
        db_configuration = config_parser['goldfinchsong.db']
        if 'db_location' in db_configuration:
            active_configuration['db_location'] = db_configuration['db_location']
    return active_configuration


@click.command()
@click.option('--action', default='post')
@click.option('--conf', default='goldfinchsong.ini')
@click.option('--images', default=None)
def run(action, conf, images):
    """
    Uploads an image tweet.

    The :class:`~.goldfinchsong.classes.Manager` class does the actual
    work; this function contributes logic for extracting configuration
    settings and creating a ``TinyDB`` instance.

    Arguments:
        action (str): An action name.
        conf (str): File path for a configuration file. By default, this
            function looks for ``goldfinchsong.ini`` under the directory from
            which the user executes the function.
        images (str): File path to a directory with images that will be uploaded by tweets.
    """
    config_parser = configparser.ConfigParser()
    # make parsing of config file names case-sensitive
    config_parser.optionxform = str
    config_parser.read(conf)
    if config_parser.has_section('goldfinchsong'):
        active_configuration = parse_configuration(config_parser)
        if action == 'post':
            logger.info('POST requested.')
            image_directory = get_image_directory(images, active_configuration)
            db = TinyDB(active_configuration['db_location'])
            manager = Manager(active_configuration['credentials'],
                              db,
                              image_directory,
                              active_configuration['text_conversions'])
            content = manager.post_tweet()
            logger.info('Sent POST with image {0} and text {1}'.format(content[0], content[1]))
        else:
            logger.error('The "{0}" action is not supported.'.format(action))
    else:
        logger.error('Twitter credentials and DB settings must be placed within ini file.')