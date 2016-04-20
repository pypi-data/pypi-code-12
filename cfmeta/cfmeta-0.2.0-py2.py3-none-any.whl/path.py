# -*- coding: utf-8 -*-

import os.path

from .exceptions import PathError

"""Path operations utilities.
"""

def get_dir_meta(fp, atts):
    """Pop path information and map to supplied atts
    """

    # Attibutes are popped from deepest directory first
    atts.reverse()

    dirname = os.path.split(fp)[0]
    meta = dirname.split('/')

    res = {}

    try:
        for key in atts:
            res[key] = meta.pop()
    except IndexError:
        raise PathError(dirname)

    return res
