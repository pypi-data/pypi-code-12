import sys

PY2 = sys.version_info < (3,)
collect_ignore = ['jaraco/translate/pmxbot.py'] if PY2 else []
