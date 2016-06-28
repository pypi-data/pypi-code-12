"""
This script updates the breeze icon theme from upstream.

This script should be used on a system which understand symlinks (i.e. not
on Windows).
"""
import os
import shutil
import subprocess


# fetch latest icons from upstream
print('fetching latest icons from upstream')
try:
    shutil.rmtree('../build')
except FileNotFoundError:
    pass
subprocess.check_call([
    'git', 'clone', 'https://github.com/NitruxSA/breeze-icon-theme.git',
    '../build/icons'])


# resolve all symlinks to make the theme works on windows
print('resolving symlinks')
i = 0
for root, dirs, files in os.walk('../build/icons/'):
    for f in files:
        path = os.path.abspath(os.path.join(os.getcwd(), root, f))
        if os.path.islink(path):
            real_path = os.path.realpath(path)
            if real_path != path:
                os.remove(path)
                shutil.copy(real_path, path, follow_symlinks=False)


# copy to resources directory
print('copying new icons to data/resources/icons')
try:
    shutil.rmtree('../data/resources/icons/Breeze')
except FileNotFoundError:
    pass
try:
    shutil.rmtree('../data/resources/icons/Breeze Dark')
except FileNotFoundError:
    pass
shutil.copytree('../build/icons/Breeze', '../data/resources/icons/Breeze',
                symlinks=True)
shutil.copytree('../build/icons/Breeze Dark',
                '../data/resources/icons/Breeze Dark',
                symlinks=True)
