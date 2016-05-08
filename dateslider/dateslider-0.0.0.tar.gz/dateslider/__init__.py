# coding: utf-8
# flake8: noqa

from ._version import *

# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        src="static",
        dest="dateslider",
        require="dateslider/index")]
