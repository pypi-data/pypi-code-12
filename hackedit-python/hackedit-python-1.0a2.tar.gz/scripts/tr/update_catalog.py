"""
This script updates an existing message catalog.

The locale must be passed as the only argument to the script.

The updated po file can be found in
``data/locale/$LOCALE/LC_MESSAGES/hackedit.po`` where $LOCALE is the locale
passed to the script (e.g. ``data/locale/fr/LC_MESSAGES/hackedit.po``)

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO::

    python3 scripts/update_catalog.py fr
"""
import subprocess
import sys

print('Extracting messages')

#: locale
locale = sys.argv[1]

print(
    subprocess.check_output([
        sys.executable, 'setup.py', 'update_catalog',
        '--domain', 'hackedit-python', '-l', locale,
        '-i', 'data/locale/hackedit-python.pot',
        '-d', 'data/locale']).decode('utf-8'))
