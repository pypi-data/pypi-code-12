"""
Extract the application messages to data/locale/hackedit.pot

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO:

python3 scripts/extract_messages.py
"""
import os
import subprocess
import sys

print('Extracting messages')

if not os.path.exists('data/locale'):
    os.mkdir('data/locale')

print(
    subprocess.check_output([
        sys.executable, 'setup.py', 'extract_messages',
        '--output-file', 'data/locale/hackedit-python.pot']).decode('utf-8'))
