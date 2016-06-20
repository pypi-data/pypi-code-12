#!/usr/bin/env python3.5
# -*- coding: utf-8 -*-
import re

name = '[A-Za-z0-9-]+'
star_or_slash = '(?:\*?|\/?)'

pattern_label = re.compile('^{} *({})$'.format(star_or_slash, name))
pattern_class = re.compile('\.({})'.format(name))
pattern_id = re.compile('#({})'.format(name))
