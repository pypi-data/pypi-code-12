#
# Copyright (c) 2015, Prometheus Research, LLC
#


import colander

from .common import ValidationError, sub_schema, LanguageTag, \
    IdentifierString, Options, LocalizedString, DescriptorList, \
    LocalizationChecker, validate_instrument_version, guard, guard_sequence, \
    MetadataCollection, RE_PRODUCT_TOKENS
from .instrument import InstrumentReference, TYPES_COMPLEX, \
    get_full_type_definition


__all__ = (
    'Interaction',
)


STEP_TYPES_ALL = (
    'question',
    'text',
)

METADATA_PROPS = {
    'author': colander.SchemaNode(
        colander.String(),
    ),
    'copyright': colander.SchemaNode(
        colander.String(),
    ),
    'homepage': colander.SchemaNode(
        colander.String(),
        validator=colander.url,
    ),
    'generator': colander.SchemaNode(
        colander.String(),
        validator=colander.Regex(RE_PRODUCT_TOKENS),
    ),
}


# pylint: disable=abstract-method


class StepType(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf(STEP_TYPES_ALL)


class TextStepOptions(colander.SchemaNode):
    text = LocalizedString()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(TextStepOptions, self).__init__(*args, **kwargs)


class QuestionStepOptions(colander.SchemaNode):
    fieldId = IdentifierString()
    text = LocalizedString()
    error = LocalizedString(missing=colander.drop)
    enumerations = DescriptorList(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(QuestionStepOptions, self).__init__(*args, **kwargs)


STEP_TYPE_OPTION_VALIDATORS = {
    'question': QuestionStepOptions(),
    'text': TextStepOptions(),
}


class Step(colander.SchemaNode):
    type = StepType()
    options = Options(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Step, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        step_type = cstruct.get('type', None)
        validator = STEP_TYPE_OPTION_VALIDATORS.get(step_type, None)
        options = cstruct.get('options', None)
        if validator:
            sub_schema(
                validator,
                node.get('options'),
                options,
            )
        elif options is not None:
            raise ValidationError(
                node.get('options'),
                '"%s" step do not accept options' % step_type,
            )


class StepList(colander.SequenceSchema):
    step = Step()
    validator = colander.Length(min=1)


class Threshold(colander.SchemaNode):
    schema_type = colander.Integer
    validator = colander.Range(min=1)


class TimeoutDetails(colander.SchemaNode):
    threshold = Threshold()
    text = LocalizedString()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(TimeoutDetails, self).__init__(*args, **kwargs)


class Timeout(colander.SchemaNode):
    warn = TimeoutDetails(missing=colander.drop)
    abort = TimeoutDetails(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Timeout, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        if not cstruct.get('warn') and not cstruct.get('abort'):
            raise ValidationError(
                node,
                'At least one of "warn" or "abort" must be defined',
            )


class Interaction(colander.SchemaNode):
    instrument = InstrumentReference()
    defaultLocalization = LanguageTag()
    defaultTimeout = Timeout(missing=colander.drop)
    steps = StepList()
    meta = MetadataCollection(
        METADATA_PROPS,
        missing=colander.drop,
    )

    def __init__(self, instrument=None, *args, **kwargs):
        self.instrument = instrument
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Interaction, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        self._check_localizations(node, cstruct)

        if not self.instrument:
            return

        validate_instrument_version(
            self.instrument,
            cstruct,
            node.get('instrument'),
        )

        self._check_fields_covered(node, cstruct)

        self._check_type_specifics(node, cstruct)

    def _check_localizations(self, node, cstruct):
        with guard(node.get('defaultTimeout')) as dtnode:
            timeouts = cstruct.get('defaultTimeout', {})
            for level in ('warn', 'abort'):
                if level in timeouts:
                    checker = LocalizationChecker(
                        dtnode.get(level),
                        cstruct['defaultLocalization'],
                    )
                    checker.ensure(
                        timeouts[level],
                        'text',
                        scope='Timeout %s Text' % level,
                    )

        for sidx, step in enumerate(cstruct['steps']):
            with guard_sequence(node, 'step', sidx) as snode:
                if 'options' not in step:  # pragma: no cover
                    return

                checker = LocalizationChecker(
                    snode.get('options'),
                    cstruct['defaultLocalization'],
                )
                options = step['options']

                checker.ensure(options, 'text', scope='Step Text')
                checker.ensure(options, 'error', scope='Step Error')

                for enumeration in options.get('enumerations', []):
                    checker.ensure_descriptor(enumeration, scope='Enumeration')

    def _check_fields_covered(self, node, cstruct):
        instrument_fields = set([
            field['id']
            for field in self.instrument['record']
        ])

        intr_fields = set()
        for step in cstruct['steps']:
            if step['type'] != 'question':
                continue

            field_id = step['options']['fieldId']
            if field_id in intr_fields:
                raise ValidationError(
                    node.get('steps'),
                    'Field "%s" is addressed by more than one question' % (
                        field_id,
                    )
                )
            else:
                intr_fields.add(field_id)

        missing = instrument_fields - intr_fields
        if missing:
            raise ValidationError(
                node.get('steps'),
                'There are Instrument fields which are missing: %s' % (
                    ', '.join(missing),
                )
            )

        extra = intr_fields - instrument_fields
        if extra:
            raise ValidationError(
                node.get('steps'),
                'There are extra fields referenced by questions: %s' % (
                    ', '.join(extra),
                )
            )

    def _get_instrument_field(self, name):
        for field in self.instrument['record']:
            if field['id'] == name:
                return field

    def _check_type_specifics(self, node, cstruct):
        for sidx, step in enumerate(cstruct['steps']):
            with guard_sequence(node, 'step', sidx) as snode:
                if step['type'] != 'question':
                    continue

                type_def = get_full_type_definition(
                    self.instrument,
                    self._get_instrument_field(
                        step['options']['fieldId'],
                    )['type'],
                )

                if type_def['base'] in TYPES_COMPLEX:
                    raise ValidationError(
                        snode.get('options'),
                        'Complex Instrument Types are not allowed in'
                        ' Interactions',
                    )

                if 'enumerations' in step['options']:
                    if type_def['base'] in ('enumeration', 'enumerationSet'):
                        described_choices = [
                            desc['id']
                            for desc in step['options']['enumerations']
                        ]
                        actual_choices = list(type_def['enumerations'].keys())
                        for described_choice in described_choices:
                            if described_choice not in actual_choices:
                                raise ValidationError(
                                    snode.get('options'),
                                    'Field "%s" describes an invalid'
                                    ' enumeration "%s"' % (
                                        step['options']['fieldId'],
                                        described_choice,
                                    ),
                                )

                    else:
                        raise ValidationError(
                            snode.get('options'),
                            'Field "%s" cannot have an enumerations'
                            ' configuration' % (
                                step['options']['fieldId'],
                            ),
                        )

