import logging

from .courtana import gender_color
from .experiment import Experiment

# FIXME should load config from a file and have different
# levels for DEV and PROD
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)-8s %(name)-24s %(message)s',
)

__all__ = ['gender_color', 'Experiment']
