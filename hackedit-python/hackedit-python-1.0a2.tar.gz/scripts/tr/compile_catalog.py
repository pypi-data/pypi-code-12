"""
This script compiles a message catalog.

The locale must be passed as the only argument to the script.

The resulting mo file will be found in
``data/locale/$LOCALE/LC_MESSAGES/hackedit.mo`` where $LOCALE is the locale
passed to the script (e.g. ``data/locale/fr/LC_MESSAGES/hackedit.mo``)

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO::

    python3 scripts/compile_catalog.py fr

"""
import subprocess
import sys

print('Extracting messages')

locale = sys.argv[1]

print(
    subprocess.check_output([
        sys.executable, 'setup.py', 'compile_catalog',
        '--domain', 'hackedit-python',
        '-l', locale, '-d', 'data/locale']).decode('utf-8'))
