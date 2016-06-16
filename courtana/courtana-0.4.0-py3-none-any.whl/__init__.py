import logging

from .courtana import GENDER_COLOR
from .experiment import Experiment

# FIXME should load config from a file and have different
# levels for DEV and PROD
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(name)-24s %(message)s',
)

__all__ = ['GENDER_COLOR', 'Experiment']
