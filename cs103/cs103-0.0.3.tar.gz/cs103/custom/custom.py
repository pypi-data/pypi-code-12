import os
import shutil

def custom_init():
    srcdir = os.path.dirname(__file__)

    src = os.path.join(srcdir, 'custom.js')
    dstdir = os.path.expanduser("~/.jupyter/custom/")
    try:
        os.makedirs(dstdir)
    except:
        pass
    shutil.copy(src, dstdir)

    src = os.path.join(srcdir, 'ipython_config.py')
    dstdir = os.path.expanduser("~/.ipython/profile_default/")
    shutil.copy(src, dstdir)
