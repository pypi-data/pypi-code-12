# -*- coding: utf-8 -*-

import logging

FORMAT = '%(asctime)-15s %(clientip)s %(levelname)s %(filename)s %(levelno)s %(message)s'
logging.basicConfig(format=FORMAT)

logger = logging.LoggerAdapter(logging.getLogger('gaia'), {"clientip": "-"})
