#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import re

_name = '[A-Za-z0-9-]+'
_star_or_slash = '(?:\*?|\/?)'

pattern_label = re.compile('^{} *({})$'.format(_star_or_slash, _name))
pattern_class = re.compile('\.({})'.format(_name))
pattern_id = re.compile('#({})'.format(_name))
