from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from textwrap import dedent


def message(source, *args, **kwargs):
    """

    :param source:
    :param kwargs:
    :return:
    """

    out = (
        dedent(source.format(*args, **kwargs).strip('\n'))
        .strip()
        .replace('\t', ' ')
        .replace('\n', ' ')
    )

    return re.sub(r'\s{2,}', ' ', out)
