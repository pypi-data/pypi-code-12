#
# Copyright (c) 2015, Prometheus Research, LLC
#


import string

import colander

from six import iteritems

from .common import ValidationError, sub_schema, LanguageTag, \
    LocalizedMapping, IdentifierString, Options, LocalizedString, \
    Descriptor as BaseDescriptor, LocalizationChecker, \
    validate_instrument_version, CompoundIdentifierString, StrictBooleanType, \
    guard_sequence, MetadataCollection, RE_PRODUCT_TOKENS
from .instrument import InstrumentReference, get_full_type_definition


__all__ = (
    'ELEMENT_TYPES_ALL',
    'EVENT_ACTIONS_ALL',
    'PARAMETER_TYPES_ALL',
    'WIDGET_SIZES_ALL',
    'WIDGET_ORIENTATIONS_ALL',
    'METADATA_PROPS',
    'STANDARD_WIDGET_DATATYPES',

    'Descriptor',
    'DescriptorList',
    'UrlList',
    'AudioSource',
    'TagList',
    'ElementType',
    'TextElementOptions',
    'AudioElementOptions',
    'Options',
    'Widget',
    'WidgetSize',
    'WidgetOrientation',
    'TextWidgetOptions',
    'TextAreaWidgetOptions',
    'RecordListWidgetOptions',
    'Hotkey',
    'HotkeyCollection',
    'EnumerationWidgetOptions',
    'Expression',
    'EventAction',
    'EventTargetList',
    'FailEventOptions',
    'EnumerationList',
    'HideEnumerationEventOptions',
    'EventList',
    'Event',
    'QuestionList',
    'QuestionElementOptions',
    'Element',
    'ElementList',
    'Page',
    'PageList',
    'ParameterType',
    'ParameterCollection',
    'Form',
)


ELEMENT_TYPES_ALL = (
    'question',
    'header',
    'text',
    'divider',
    'audio',
)


EVENT_ACTIONS_ALL = (
    'hide',
    'disable',
    'hideEnumeration',
    'fail',
)


PARAMETER_TYPES_ALL = (
    'text',
    'numeric',
    'boolean',
)


WIDGET_SIZES_ALL = (
    'small',
    'medium',
    'large',
)


WIDGET_ORIENTATIONS_ALL = (
    'vertical',
    'horizontal',
)


STANDARD_WIDGET_DATATYPES = {
    'inputText': [
        'text',
    ],
    'inputNumber': [
        'integer',
        'float',
    ],
    'textArea': [
        'text',
    ],
    'radioGroup': [
        'enumeration',
        'boolean',
    ],
    'checkGroup': [
        'enumerationSet',
    ],
    'dropDown': [
        'enumeration',
        'boolean',
    ],
    'datePicker': [
        'date',
    ],
    'timePicker': [
        'time',
    ],
    'dateTimePicker': [
        'dateTime',
    ],
    'recordList': [
        'recordList',
    ],
    'matrix': [
        'matrix',
    ],
}


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


class UrlList(colander.SequenceSchema):
    url = colander.SchemaNode(colander.String())
    validator = colander.Length(min=1)


class AudioSource(LocalizedMapping):
    def __init__(self, *args, **kwargs):
        super(AudioSource, self).__init__(
            UrlList(),
            *args,
            **kwargs
        )


class TagList(colander.SequenceSchema):
    tag = IdentifierString()
    validator = colander.Length(min=1)


class ElementType(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf(ELEMENT_TYPES_ALL)


class TextElementOptions(colander.SchemaNode):
    text = LocalizedString()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(TextElementOptions, self).__init__(*args, **kwargs)


class AudioElementOptions(colander.SchemaNode):
    source = AudioSource()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(AudioElementOptions, self).__init__(*args, **kwargs)


class WidgetSize(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf(WIDGET_SIZES_ALL)


class WidgetOrientation(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf(WIDGET_ORIENTATIONS_ALL)


class TextWidgetOptions(colander.SchemaNode):
    width = WidgetSize(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='ignore')
        super(TextWidgetOptions, self).__init__(*args, **kwargs)


class TextAreaWidgetOptions(TextWidgetOptions):
    height = WidgetSize(missing=colander.drop)


class RecordListWidgetOptions(colander.SchemaNode):
    addLabel = LocalizedString(missing=colander.drop)
    removeLabel = LocalizedString(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='ignore')
        super(RecordListWidgetOptions, self).__init__(*args, **kwargs)


class Hotkey(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf(string.digits)


class HotkeyCollection(colander.SchemaNode):
    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='preserve')
        super(HotkeyCollection, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        cstruct = cstruct or {}
        if len(cstruct) == 0:
            raise ValidationError(
                node,
                'At least one Hotkey must be defined',
            )

        for _, hotkey in iteritems(cstruct):
            sub_schema(Hotkey, node, hotkey)


class EnumerationWidgetOptions(colander.SchemaNode):
    hotkeys = HotkeyCollection(missing=colander.drop)
    autoHotkeys = colander.SchemaNode(
        StrictBooleanType(),
        missing=colander.drop,
    )
    orientation = WidgetOrientation(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='ignore')
        super(EnumerationWidgetOptions, self).__init__(*args, **kwargs)


WIDGET_TYPE_OPTION_VALIDATORS = {
    'inputText': TextWidgetOptions(),
    'inputNumber': TextWidgetOptions(),
    'textArea': TextAreaWidgetOptions(),
    'recordList': RecordListWidgetOptions(),
    'radioGroup': EnumerationWidgetOptions(),
    'checkGroup': EnumerationWidgetOptions(),
}


class Widget(colander.SchemaNode):
    type = colander.SchemaNode(colander.String())
    options = Options(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Widget, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        widget_type = cstruct.get('type', None)
        validator = WIDGET_TYPE_OPTION_VALIDATORS.get(widget_type, None)
        options = cstruct.get('options', None)
        if validator and options:
            sub_schema(
                validator,
                node.get('options'),
                options,
            )


class Expression(colander.SchemaNode):
    schema_type = colander.String


class EventAction(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf(EVENT_ACTIONS_ALL)


class EventTargetList(colander.SequenceSchema):
    target = CompoundIdentifierString()
    validator = colander.Length(min=1)


class FailEventOptions(colander.SchemaNode):
    text = LocalizedString()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(FailEventOptions, self).__init__(*args, **kwargs)


class EnumerationList(colander.SequenceSchema):
    enumeration = colander.SchemaNode(colander.String())
    validator = colander.Length(min=1)


class HideEnumerationEventOptions(colander.SchemaNode):
    enumerations = EnumerationList()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(HideEnumerationEventOptions, self).__init__(*args, **kwargs)


EVENT_ACTION_OPTION_VALIDATORS = {
    'fail': FailEventOptions(),
    'hideEnumeration': HideEnumerationEventOptions(),
}


class Event(colander.SchemaNode):
    trigger = Expression()
    action = EventAction()
    targets = EventTargetList(missing=colander.drop)
    options = Options(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Event, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        action = cstruct.get('action', None)
        validator = EVENT_ACTION_OPTION_VALIDATORS.get(action, None)
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
                '"%s" events do not accept options' % action,
            )


class EventList(colander.SequenceSchema):
    event = Event()
    validator = colander.Length(min=1)


class QuestionList(colander.SchemaNode):
    validator = colander.Length(min=1)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Sequence()
        super(QuestionList, self).__init__(*args, **kwargs)
        self.add(QuestionElementOptions(
            allow_complex=False,
            name='question',
        ))


class Descriptor(BaseDescriptor):
    audio = AudioSource(missing=colander.drop)


class DescriptorList(colander.SequenceSchema):
    descriptor = Descriptor()
    validator = colander.Length(min=1)


class QuestionElementOptions(colander.SchemaNode):
    fieldId = IdentifierString()
    text = LocalizedString()
    audio = AudioSource(missing=colander.drop)
    help = LocalizedString(missing=colander.drop)
    error = LocalizedString(missing=colander.drop)
    enumerations = DescriptorList(missing=colander.drop)
    widget = Widget(missing=colander.drop)
    events = EventList(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        self.allow_complex = kwargs.pop('allow_complex', True)
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(QuestionElementOptions, self).__init__(*args, **kwargs)
        if self.allow_complex:
            self.add(QuestionList(
                name='questions',
                missing=colander.drop,
            ))
            self.add(DescriptorList(
                name='rows',
                missing=colander.drop,
            ))


ELEMENT_TYPE_OPTION_VALIDATORS = {
    'question': QuestionElementOptions(),
    'text': TextElementOptions(),
    'header': TextElementOptions(),
    'audio': AudioElementOptions(),
}


class Element(colander.SchemaNode):
    type = ElementType()
    options = Options(missing=colander.drop)
    tags = TagList(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Element, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        element_type = cstruct.get('type', None)
        validator = ELEMENT_TYPE_OPTION_VALIDATORS.get(element_type, None)
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
                '"%s" elements do not accept options' % element_type,
            )

        tags = cstruct.get('tags', [])
        if tags:
            duplicates = list(set([x for x in tags if tags.count(x) > 1]))
            if duplicates:
                raise ValidationError(
                    node.get('tags'),
                    'Tags can only be assigned to an element once:'
                    ' %s' % (
                        ', '.join(duplicates)
                    ),
                )


class ElementList(colander.SequenceSchema):
    element = Element()
    validator = colander.Length(min=1)


class Page(colander.SchemaNode):
    id = IdentifierString()  # pylint: disable=invalid-name
    elements = ElementList()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Page, self).__init__(*args, **kwargs)


class PageList(colander.SequenceSchema):
    page = Page()

    def validator(self, node, cstruct):
        if len(cstruct) < 1:
            raise ValidationError(
                node,
                'Shorter than minimum length 1',
            )

        ids = [page['id'] for page in cstruct]
        duplicates = list(set([x for x in ids if ids.count(x) > 1]))
        if duplicates:
            raise ValidationError(
                node,
                'Page IDs must be unique: %s' % ', '.join(duplicates),
            )


class ParameterType(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf(PARAMETER_TYPES_ALL)


class ParameterOptions(colander.SchemaNode):
    type = ParameterType()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(ParameterOptions, self).__init__(*args, **kwargs)


class ParameterCollection(colander.SchemaNode):
    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='preserve')
        super(ParameterCollection, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        cstruct = cstruct or {}
        if len(cstruct) == 0:
            raise ValidationError(
                node,
                'At least one key/value pair must be defined',
            )

        for name, options in iteritems(cstruct):
            sub_schema(IdentifierString, node, name)
            sub_schema(ParameterOptions, node, options)


class Form(colander.SchemaNode):
    instrument = InstrumentReference()
    defaultLocalization = LanguageTag()
    title = LocalizedString(missing=colander.drop)
    pages = PageList()
    parameters = ParameterCollection(missing=colander.drop)
    meta = MetadataCollection(
        METADATA_PROPS,
        missing=colander.drop,
    )

    def __init__(self, instrument=None, *args, **kwargs):
        self.instrument = instrument
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Form, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        self._check_localizations(node, cstruct)

        if not self.instrument:
            self._standalone_checks(node, cstruct)
        else:
            self._instrument_checks(node, cstruct)

    def _check_tags(self, node, element, invalid_tags):
        if element.get('tags', []):
            tags = set(element['tags'])
            duped = invalid_tags & tags
            if duped:
                raise ValidationError(
                    node.get('tags'),
                    'Tag(s) are duplicates of existing'
                    ' identifiers: %s' % (
                        ', '.join(sorted(duped)),
                    )
                )

    def _standalone_checks(self, node, cstruct):
        invalid_tags = set([page['id'] for page in cstruct['pages']])

        for pidx, page in enumerate(cstruct['pages']):
            with guard_sequence(node, 'page', pidx) as enode:
                for eidx, element in enumerate(page['elements']):
                    with guard_sequence(enode, 'element', eidx) as onode:
                        self._check_tags(onode, element, invalid_tags)

    def _instrument_checks(self, node, cstruct):
        validate_instrument_version(
            self.instrument,
            cstruct,
            node.get('instrument'),
        )

        self._check_fields_covered(node, cstruct)

        invalid_tags = [page['id'] for page in cstruct['pages']]
        invalid_tags.extend([
            field['id']
            for field in self.instrument['record']
        ])
        invalid_tags = set(invalid_tags)

        for pidx, page in enumerate(cstruct['pages']):
            with guard_sequence(node, 'page', pidx) as enode:
                for eidx, element in enumerate(page['elements']):
                    with guard_sequence(enode, 'element', eidx) as onode:
                        self._check_tags(onode, element, invalid_tags)

                        if element['type'] != 'question':
                            continue
                        self._check_type_specifics(
                            onode.get('options'),
                            element.get('options', {}),
                        )

    def _check_localizations(self, node, cstruct):
        checker = LocalizationChecker(node, cstruct['defaultLocalization'])
        checker.ensure(cstruct, 'title', node=node.get('title'))

        def _ensure_element(element, subnode):
            if 'options' not in element:
                return
            options = element['options']

            checker = LocalizationChecker(
                subnode.get('options'),
                cstruct['defaultLocalization'],
            )
            checker.ensure(options, 'text', scope='Element Text')
            checker.ensure(options, 'help', scope='Element Help')
            checker.ensure(options, 'error', scope='Element Error')
            checker.ensure(options, 'audio', scope='Element Audio')
            checker.ensure(options, 'source', scope='Audio Source')

            for question in options.get('questions', []):
                _ensure_element(question, subnode)
            for enumeration in options.get('enumerations', []):
                checker.ensure_descriptor(enumeration, scope='Enumeration')
            for row in options.get('rows', []):
                checker.ensure_descriptor(row, scope='Matrix Row')
            for event in options.get('events', []):
                checker.ensure(
                    event.get('options', {}),
                    'text',
                    scope='Event Text',
                    node=subnode.get('options').get('events'),
                )

        for pidx, page in enumerate(cstruct['pages']):
            with guard_sequence(node, 'page', pidx) as enode:
                for eidx, element in enumerate(page['elements']):
                    with guard_sequence(enode, 'element', eidx) as onode:
                        _ensure_element(element, onode)

    def _check_fields_covered(self, node, cstruct):
        instrument_fields = set([
            field['id']
            for field in self.instrument['record']
        ])

        form_fields = set()
        for pidx, page in enumerate(cstruct['pages']):
            with guard_sequence(node, 'page', pidx) as enode:
                for eidx, element in enumerate(page['elements']):
                    if element['type'] != 'question':
                        continue

                    with guard_sequence(enode, 'element', eidx):
                        field_id = element['options']['fieldId']
                        if field_id in form_fields:
                            raise ValidationError(
                                node,
                                'Field "%s" is addressed by more than one'
                                ' question' % (
                                    field_id,
                                )
                            )
                        else:
                            form_fields.add(field_id)

        missing = instrument_fields - form_fields
        if missing:
            raise ValidationError(
                node,
                'There are Instrument fields which are missing: %s' % (
                    ', '.join(missing),
                )
            )

        extra = form_fields - instrument_fields
        if extra:
            raise ValidationError(
                node,
                'There are extra fields referenced by questions: %s' % (
                    ', '.join(extra),
                )
            )

    def _get_instrument_field_type(self, name, record=None):
        record = record or self.instrument['record']
        for field in record:
            if field['id'] == name:
                return get_full_type_definition(
                    self.instrument,
                    field['type'],
                )

    def _check_type_specifics(self, node, options, record=None):
        type_def = self._get_instrument_field_type(
            options['fieldId'],
            record=record,
        )

        if 'enumerations' in options:
            if type_def['base'] in ('enumeration', 'enumerationSet'):
                described_choices = [
                    desc['id']
                    for desc in options['enumerations']
                ]
                actual_choices = list(type_def['enumerations'].keys())
                for described_choice in described_choices:
                    if described_choice not in actual_choices:
                        raise ValidationError(
                            node,
                            'Field "%s" describes an invalid'
                            ' enumeration "%s"' % (
                                options['fieldId'],
                                described_choice,
                            ),
                        )

            else:
                raise ValidationError(
                    node,
                    'Field "%s" cannot have an enumerations'
                    ' configuration' % (
                        options['fieldId'],
                    ),
                )

        self._check_matrix(node, type_def, options)
        self._check_subquestions(node, type_def, options)
        self._check_widget_assignment(node, type_def, options)

    def _check_widget_assignment(self, node, type_def, options):
        widget = options.get('widget', {}).get('type')
        if not widget:
            return

        if widget in STANDARD_WIDGET_DATATYPES \
                and type_def['base'] not in STANDARD_WIDGET_DATATYPES[widget]:
            raise ValidationError(
                node,
                'Standard widget "%s" cannot be used with fields of type'
                ' "%s"' % (
                    widget,
                    type_def['base'],
                ),
            )

    def _check_matrix(self, node, type_def, options):
        if type_def['base'] == 'matrix':
            instrument_rows = set([
                row['id']
                for row in type_def['rows']
            ])

            form_rows = set()
            for row in options.get('rows', []):
                if row['id'] in form_rows:
                    raise ValidationError(
                        node,
                        'Row %s is addressed by more than one descriptor in'
                        ' %s' % (
                            row['id'],
                            options['fieldId'],
                        ),
                    )
                else:
                    form_rows.add(row['id'])

            missing = instrument_rows - form_rows
            if missing:
                raise ValidationError(
                    node,
                    'There are missing rows in %s: %s' % (
                        options['fieldId'],
                        ', '.join(missing),
                    )
                )

            extra = form_rows - instrument_rows
            if extra:
                raise ValidationError(
                    node,
                    'There are extra rows referenced by %s: %s' % (
                        options['fieldId'],
                        ', '.join(extra),
                    )
                )

        elif 'rows' in options:
            raise ValidationError(
                node,
                'Field "%s" cannot have a rows configuration' % (
                    options['fieldId'],
                ),
            )

    def _check_subquestions(self, node, type_def, options):
        if type_def['base'] in ('matrix', 'recordList'):
            record = type_def[
                'columns' if type_def['base'] == 'matrix' else 'record'
            ]
            instrument_fields = set([field['id'] for field in record])

            form_fields = set()
            for subfield in options.get('questions', []):
                if subfield['fieldId'] in form_fields:
                    raise ValidationError(
                        node,
                        'Subfield %s is addressed by more than one question in'
                        ' %s' % (
                            subfield['fieldId'],
                            options['fieldId'],
                        ),
                    )
                else:
                    form_fields.add(subfield['fieldId'])

            missing = instrument_fields - form_fields
            if missing:
                raise ValidationError(
                    node,
                    'There are missing subfields in %s: %s' % (
                        options['fieldId'],
                        ', '.join(missing),
                    )
                )

            extra = form_fields - instrument_fields
            if extra:
                raise ValidationError(
                    node,
                    'There are extra subfields referenced by %s: %s' % (
                        options['fieldId'],
                        ', '.join(extra),
                    )
                )

            for question in options['questions']:
                self._check_type_specifics(node, question, record=record)

        elif 'questions' in options:
            raise ValidationError(
                node,
                'Field "%s" cannot have a questions configuration' % (
                    options['fieldId'],
                ),
            )

