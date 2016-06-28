"""
This script compiles the ui files into python scripts.

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO:

python3 scripts/build_ui.py
"""
import subprocess
import sys

print('Compiling *.ui files to python scripts...')

print(
    subprocess.check_output([sys.executable, 'setup.py', 'build_ui']).decode(
        'utf-8'))
