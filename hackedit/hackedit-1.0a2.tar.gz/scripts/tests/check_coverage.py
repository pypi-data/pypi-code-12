"""
Run tests and check coverage of the whole application.

Requires pytest-cov.

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO:

python3 scripts/check_api.py

"""
import os
import sys

os.environ['PYTEST_QT_API'] = 'pyqt5'

os.system('%s setup.py test -a "--cov hackedit --cov-report term '
          '--cov-report html"' % sys.executable)
