# -*- coding: utf-8 -*-
from context import context
from context import localcontext
from logger import logger


if 'theContext' not in globals():
    theContext = localcontext()
