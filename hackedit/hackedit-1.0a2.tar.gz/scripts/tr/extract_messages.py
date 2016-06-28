"""
Extract the application messages to data/locale/hackedit.pot

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO:

python3 scripts/extract_messages.py
"""
import subprocess
import sys

print('Extracting messages')

print(
    subprocess.check_output([
        sys.executable, 'setup.py', 'extract_messages',
        '--output-file', 'data/locale/hackedit.pot']).decode('utf-8'))
