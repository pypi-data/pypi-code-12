from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import math


def unzip(values, raw=False):
    """

    :param values:

    :param raw: (optional) If True, the values and uncertainty lists will be
        raw instead the standard truncated formats specified by error
        propagation rules
    :return: tuple containing a list of values and a list of uncertainties
    """

    vals = []
    uncs = []

    if isinstance(values[0], (list, tuple)):
        values = values[0]

    for v in values:
        vals.append(v.raw if raw else v.value)
        uncs.append(v.raw_uncertainty if raw else v.uncertainty)

    return vals, uncs


def deviations(expected, values):
    """

    :param expected:
    :param values:
    :return:
    """

    out = []

    if hasattr(expected, 'raw_uncertainty'):
        for v in values:
            err = math.sqrt(
                v.raw_uncertainty ** 2 +
                expected.raw_uncertainty ** 2
            )
            out.append(abs(v.raw - expected.raw) / err)
    else:
        for v in values:
            out.append(abs(v.value - expected) / v.uncertainty)

    return out
