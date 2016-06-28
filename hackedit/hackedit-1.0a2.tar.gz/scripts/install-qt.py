"""
Simple script to install PyQt5 in AppVeyor.
"""
from __future__ import print_function
import os
import subprocess
import urllib.request


def fix_registry(python_ver):
    """Update install path on windows registry so PyQt installation installs
    at the correct location.
    python_ver must be "34", "27", etc.
    """
    import winreg
    arch = os.environ['PYTHON_ARCH']
    if arch == '64':
        python_dir = r'C:\Python%s-x64' % python_ver
    else:
        python_dir = r'C:\Python%s' % python_ver
    print("Fixing registry %s..." % python_ver)
    assert os.path.isdir(python_dir)
    registry_key = r'Software\Python\PythonCore\%s.%s' % (
        python_ver[0], python_ver[1])
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                        registry_key, 0,
                        winreg.KEY_WRITE) as key:
        winreg.SetValue(key, 'InstallPath', winreg.REG_SZ, python_dir)

base_url = 'http://downloads.sourceforge.net/project/pyqt/'
downloads = {
    'py34-pyqt5-32': 'PyQt5/PyQt-5.5.1/PyQt5-5.5.1-gpl-Py3.4-Qt5.5.1-x32.exe',
    'py34-pyqt5-64': 'PyQt5/PyQt-5.5.1/PyQt5-5.5.1-gpl-Py3.4-Qt5.5.1-x64.exe',
}

fix_registry('34')
arch = os.environ['PYTHON_ARCH']
caption = 'py34-pyqt5-%s' % arch
url = downloads[caption]
print("Downloading %s..." % caption)
installer = r'C:\install-%s.exe' % caption
urllib.request.urlretrieve(base_url + url, installer)
print('Installing %s...' % caption)
subprocess.check_call([installer, '/S'])
