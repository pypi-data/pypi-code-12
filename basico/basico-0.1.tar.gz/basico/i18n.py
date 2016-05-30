#!/usr/bin/python3
# -*- coding: utf-8 -*-
# File: i18nb.py
# Author: Tomás Vírseda
# License: GPL v3
# Description: i18n module

import os
import gettext

base_dir = os.path.abspath(os.path.dirname(__file__))
d = '/usr/local/share' if 'local' in base_dir.split('/') else '/usr/share'
gettext.bindtextdomain('genxword', os.path.join(d, 'locale'))
gettext.textdomain('basico')
_ = gettext.gettext
