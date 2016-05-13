# -*- coding: utf-8 -*-


import os

from ..utils import run

installer_tmpl_path = os.path.join(os.path.dirname(__file__), 'ruby_installer.sh')
with open(installer_tmpl_path) as f:
    INSTALLER = f.read()
del installer_tmpl_path

def build(conf):
    run('bundle package --path=$DATA_DIR')
