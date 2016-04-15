#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
This module contains the actual computation of :abbr:`IQMs (image quality
metrics)` included within MRIQC.

.. note ::

  Most of the :abbr:`IQMs (image quality metrics)` in this module are adapted, derived or reproduced
  from the :abbr:`QAP (quality assessment protocols)` project [QAP]_.

"""

from .anatomical import *  # pylint: disable=wildcard-import
from .functional import *  # pylint: disable=wildcard-import
