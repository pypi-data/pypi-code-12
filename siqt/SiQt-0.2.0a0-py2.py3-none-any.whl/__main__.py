# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from .siqt.importers import use

import os

pars = {'mode': 'compatible'}
if 'SIQT_BACKEND_FORCE' in os.environ:
    pars['backend_name'] = os.environ['SIQT_BACKEND_FORCE']
    pars['force'] = True
elif 'SIQT_BACKEND' in os.environ:
    pars['backend_name'] = os.environ['SIQT_BACKEND']
    pars['force'] = False
else:
    raise ValueError('Environemental variables SIQT_BACKEND or SIQT_BACKEND_FORCE not found!')

if 'SIQT_MODE' in os.environ:
    pars['mode'] = os.environ['SIQT_MODE']

use(**pars)
