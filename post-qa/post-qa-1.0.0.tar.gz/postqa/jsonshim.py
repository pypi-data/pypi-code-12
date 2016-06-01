"""Tools for shimming the JSON output from validate_drp into the simpler
JSON schema expected by the SQuaSH dashboard's POST /api/jobs/ endpoint.
"""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA


def shim_validate_drp(vdrp_json,
                      accepted_metrics=('PA1', 'AM1', 'AM2', 'AM3')):
    """Convert JSON structure from validate DRP into the JSON expected by
    SQuaSH's POST /api/jobs/ endpoint.

    This makes a full job document, but only populates the ``measurements``
    field.
    """
    job_json = {}

    measurements = []
    for vdrp_measurement_doc in vdrp_json['measurements']:
        if vdrp_measurement_doc['metric']['name'] not in accepted_metrics:
            continue
        measurements.append(shim_vdrp_measurement(vdrp_measurement_doc))
    job_json['measurements'] = measurements

    return job_json


def shim_vdrp_measurement(vdrp_doc):
    """Shim a measurement document from validate_drp to a measurement document
    expected by SQuaSH.
    """
    output_doc = {
        'metric': vdrp_doc['metric']['name'],
        'value': vdrp_doc['value']['value']
    }
    return output_doc
