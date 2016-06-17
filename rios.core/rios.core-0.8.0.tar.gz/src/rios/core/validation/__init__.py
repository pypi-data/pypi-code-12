#
# Copyright (c) 2015, Prometheus Research, LLC
#


import json

import six

from .common import ValidationError
from .assessment import Assessment
from .calculationset import CalculationSet
from .form import Form
from .instrument import Instrument, get_full_type_definition
from .interaction import Interaction


__all__ = (
    'ValidationError',
    'validate_instrument',
    'validate_assessment',
    'validate_calculationset',
    'validate_form',
    'validate_interaction',
    'get_full_type_definition',
)


def _get_struct(src):
    if isinstance(src, six.string_types):
        src = json.loads(src, encoding='utf-8')
    elif hasattr(src, 'read'):
        src = json.load(src, encoding='utf-8')
    return src


def validate_instrument(instrument):
    """
    Validates the input against the RIOS Instrument Definition
    specification.

    :param instrument: The Instrument Definition to validate
    :type instrument: JSON string, dict, or file-like object
    :raises ValidationError: If the input fails any part of the specification
    """

    instrument = _get_struct(instrument)
    validator = Instrument()
    validator.deserialize(instrument)


def validate_assessment(assessment, instrument=None):
    """
    Validates the input against the RIOS Assessment Document specification.

    :param assessment: The Assessment Document to validate
    :type assessment: JSON string, dict, or file-like object
    :param instrument:
        The Instrument Definition to validate the Assessment against. If not
        specified, this defaults to ``None``, which means that only the basic
        structure of the Assessment will be validated -- not its conformance to
        the Instrument.
    :type instrument: JSON string, dict, or file-like object
    :raises ValidationError: If the input fails any part of the specification
    """

    assessment = _get_struct(assessment)
    if instrument:
        instrument = _get_struct(instrument)
        validate_instrument(instrument)
    validator = Assessment(instrument=instrument)
    validator.deserialize(assessment)


def validate_calculationset(calculationset, instrument=None):
    """
    Validates the input against the RIOS Calculation Set Definition
    specification.

    :param form: The Calculation Set Definition to validate
    :type form: JSON string, dict, or file-like object
    :param instrument:
        The Instrument Definition to validate the Calculation Set against. If
        not specified, this defaults to ``None``, which means that only the
        basic structure of the Calculation Set will be validated -- not its
        conformance to the Instrument.
    :type instrument: JSON string, dict, or file-like object
    :raises ValidationError: If the input fails any part of the specification
    """

    calculationset = _get_struct(calculationset)
    if instrument:
        instrument = _get_struct(instrument)
        validate_instrument(instrument)
    validator = CalculationSet(instrument=instrument)
    validator.deserialize(calculationset)


def validate_form(form, instrument=None):
    """
    Validates the input against the RIOS Web Form Configuration
    specification.

    :param form: The Web Form Configuration to validate
    :type form: JSON string, dict, or file-like object
    :param instrument:
        The Instrument Definition to validate the Form against. If not
        specified, this defaults to ``None``, which means that only the basic
        structure of the Form will be validated -- not its conformance to
        the Instrument.
    :type instrument: JSON string, dict, or file-like object
    :raises ValidationError: If the input fails any part of the specification
    """

    form = _get_struct(form)
    if instrument:
        instrument = _get_struct(instrument)
        validate_instrument(instrument)
    validator = Form(instrument=instrument)
    validator.deserialize(form)


def validate_interaction(interaction, instrument=None):
    """
    Validates the input against the RIOS SMS Interaction Configuration
    specification.

    :param interaction: The SMS Interaction Configuration to validate
    :type interaction: JSON string, dict, or file-like object
    :param instrument:
        The Instrument Definition to validate the Interaction against. If not
        specified, this defaults to ``None``, which means that only the basic
        structure of the Interaction will be validated -- not its conformance
        to the Instrument.
    :type instrument: JSON string, dict, or file-like object
    :raises ValidationError: If the input fails any part of the specification
    """

    interaction = _get_struct(interaction)
    if instrument:
        instrument = _get_struct(instrument)
        validate_instrument(instrument)
    validator = Interaction(instrument=instrument)
    validator.deserialize(interaction)

