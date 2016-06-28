"""
Checks PEP8 compliance.

Requires pytest-pep8.

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO:

python3 scripts/check_pep8.py
"""
import os
import sys

os.environ['PYTEST_QT_API'] = 'pyqt5'

os.system('%s setup.py test -a "--flake8 -m flake8"' % sys.executable)
