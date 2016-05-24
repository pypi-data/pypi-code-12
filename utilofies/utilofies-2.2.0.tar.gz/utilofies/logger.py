# -*- encoding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import logging
from utilofies.stdlib import ExtraFormatter

NAME = 'utilofies'
LEVEL = logging.INFO
FORMAT = '%(asctime)s: %(levelname)s: %(funcName)s (%(thread)d): %(message)s'

logger = logging.getLogger(NAME)
logger.root.handlers[0].setFormatter(ExtraFormatter(fmt=FORMAT))
logger.setLevel(LEVEL)
