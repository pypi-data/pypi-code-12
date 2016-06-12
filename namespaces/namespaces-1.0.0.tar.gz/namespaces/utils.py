from __future__ import unicode_literals
import re

def isidentifier(string):
  '''Backport of python3's str#isidentifier.
  Checks that the string begins with an alphabetic character or underscore and
  contains only alphanumeric characters and underscores.
  '''
  return bool(re.match(r'^[^\d\W]\w*$', string))
