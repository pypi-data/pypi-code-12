################################################################
# xmldirector.dita
# (C) 2016,  Andreas Jung, www.zopyx.com, Tuebingen, Germany
################################################################


from __future__ import print_function

import os
import stat
import tempfile
import shutil
import zipfile

import requests
from clint.textui import progress

from xmldirector.dita import util


cwd = os.path.abspath(os.path.dirname(__file__))
target_directory = os.path.join(cwd, 'converters')

DITA = 'https://github.com/dita-ot/dita-ot/releases/download/2.3.1/dita-ot-2.3.1.zip'
DITAC = 'http://www.xmlmind.com/ditac/_download/ditac-2_6_1.zip'


def install_converter(converter='dita'):

    java = util.which('java')
    java2 = os.path.exists(os.path.join(os.environ.get('JAVA_HOME'), 'bin', 'java'))
    if not java and not java2:
        raise RuntimeError('Please check your Java installation for $JAVA_HOME settings')

    url = DITA if converter == 'dita' else DITAC
    print('Downloading {}'.format(url))

    out_fn = tempfile.mktemp(suffix='.zip')
    r = requests.get(url, stream=True)
    with open(out_fn, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
            if chunk:
                f.write(chunk)
                f.flush()

    print('Installing {}'.format(url))
    with zipfile.ZipFile(out_fn, 'r') as fp:
        for name in fp.namelist():
            if name.endswith('/'):
                continue
            name2 = '/'.join(name.split('/')[1:]) # chop of leading dirname
            target_fn = os.path.join(target_directory, converter, name2)
            target_dir = os.path.dirname(target_fn)
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            with open(target_fn, 'wb') as fp_out:
                fp_out.write(fp.read(name))
    
    for dirpath, dirnames, filenames in os.walk(target_directory):
        for filename in filenames:
            filename = os.path.join(dirpath, filename)
            if '/bin/' in filename:
                st = os.stat(filename)
                os.chmod(filename, st.st_mode | stat.S_IEXEC)

    return out_fn


def main():

    if os.path.exists(target_directory):
        shutil.rmtree(target_directory)
    os.makedirs(target_directory)

    install_converter('dita')
    install_converter('ditac')

    print('Done')

if __name__ == '__main__':
    main()
