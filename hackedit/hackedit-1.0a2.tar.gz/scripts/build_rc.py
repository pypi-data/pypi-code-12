"""
This script compiles hackedit.qrc file into a python script

YOU SHOULD START THIS SCRIPT FROM THE ROOT DIR OF THE SOURCE REPO:

python3 scripts/build_rc.py
"""
import subprocess


print('Compiling hackedit.qrc to a python script...')

print(
    subprocess.check_output([
        'pyrcc5', 'data/resources/hackedit.qrc', '-o',
        'hackedit/app/forms/hackedit_rc.py']).decode('utf-8'))
