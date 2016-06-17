#
# Copyright (c) 2015, Prometheus Research, LLC
#


import re

from copy import deepcopy

import colander

from six import iteritems, iterkeys, string_types

from .common import ValidationError, RE_IDENTIFIER, IdentifierString, \
    sub_schema, AnyType, OneOfType, StrictBooleanType, OptionalStringType, \
    MetadataCollection, RE_PRODUCT_TOKENS


__all__ = (
    'TYPES_SIMPLE',
    'TYPES_COMPLEX',
    'TYPES_ALL',
    'CONSTRAINTS_ALL',
    'TYPES_CONSTRAINED',
    'TYPES_CONSTRAINED_REQUIRED',
    'RE_ENUMERATION_ID',
    'METADATA_PROPS',

    'get_full_type_definition',

    'InstrumentIdentifier',
    'InstrumentReference',
    'Version',
    'Description',
    'EnumerationIdentifier',
    'Enumeration',
    'EnumerationCollection',
    'BoundConstraint',
    'IntegerBoundConstraint',
    'Column',
    'ColumnCollection',
    'Row',
    'RowCollection',
    'TypeDefinition',
    'RequiredOptionalField',
    'InstrumentTypes',
    'FieldType',
    'Field',
    'Record',
    'Instrument',
)


TYPES_SIMPLE = (
    'text',
    'integer',
    'float',
    'boolean',
    'enumeration',
    'enumerationSet',
    'date',
    'time',
    'dateTime',
)

TYPES_COMPLEX = (
    'recordList',
    'matrix',
)

TYPES_ALL = TYPES_SIMPLE + TYPES_COMPLEX

CONSTRAINTS_ALL = (
    'range',
    'length',
    'pattern',
    'enumerations',
    'record',
    'columns',
    'rows',
)

TYPES_CONSTRAINED = {
    'integer': [
        'range',
    ],

    'float': [
        'range',
    ],

    'date': [
        'range',
    ],

    'time': [
        'range',
    ],

    'dateTime': [
        'range',
    ],

    'text': [
        'length',
        'pattern',
    ],

    'enumeration': [
        'enumerations',
    ],

    'enumerationSet': [
        'length',
        'enumerations',
    ],

    'recordList': [
        'length',
        'record',
    ],

    'matrix': [
        'rows',
        'columns',
    ],
}

TYPES_CONSTRAINED_REQUIRED = {
    'enumeration': [
        'enumerations',
    ],

    'enumerationSet': [
        'enumerations',
    ],

    'recordList': [
        'record',
    ],

    'matrix': [
        'rows',
        'columns',
    ],
}

RANGE_CONSTRAINT_TYPES = {
    'integer': colander.Integer(),
    'float': colander.Float(),
    'date': colander.Date(),
    'time': colander.Time(),
    'dateTime': colander.DateTime(),
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


RE_VERSION = re.compile(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)')
RE_ENUMERATION_ID = re.compile(
    r'^(?:[a-z0-9]{1,2}|[a-z0-9](?:[a-z0-9]|[_-](?![_-]))+[a-z0-9])$'
)


# pylint: disable=abstract-method


class InstrumentIdentifier(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.url


class Version(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.Regex(RE_VERSION)


class InstrumentReference(colander.SchemaNode):
    id = InstrumentIdentifier()  # pylint: disable=invalid-name
    version = Version()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(InstrumentReference, self).__init__(*args, **kwargs)


class Description(colander.SchemaNode):
    schema_type = OptionalStringType
    validator = colander.Length(min=1)
    missing = colander.drop


class Enumeration(colander.SchemaNode):
    description = Description()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Enumeration, self).__init__(*args, **kwargs)


class EnumerationIdentifier(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.Regex(RE_ENUMERATION_ID)


class EnumerationCollection(colander.SchemaNode):
    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='preserve')
        super(EnumerationCollection, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        cstruct = cstruct or {}
        if len(cstruct) == 0:
            raise ValidationError(
                node,
                'At least one Enumeration must be defined',
            )

        for enum_id, enum_def in iteritems(cstruct):
            sub_schema(EnumerationIdentifier, node, enum_id)
            if enum_def is not None:
                sub_schema(Enumeration, node, enum_def)


class BoundConstraint(colander.SchemaNode):
    def __init__(self, schema_type=None, **kwargs):
        self.schema_type = schema_type
        schema_type = schema_type or AnyType()
        super(BoundConstraint, self).__init__(
            colander.Mapping(unknown='raise'),
            colander.SchemaNode(
                schema_type,
                name='min',
                missing=colander.drop,
            ),
            colander.SchemaNode(
                schema_type,
                name='max',
                missing=colander.drop,
            ),
            **kwargs
        )

    def validator(self, node, cstruct):
        if len(cstruct) < 1:
            raise ValidationError(
                node,
                'At least one bound must be specified',
            )

        if self.schema_type:
            min_value = cstruct.get('min', None)
            max_value = cstruct.get('max', None)
            if min_value is not None \
                    and max_value is not None \
                    and min_value > max_value:
                raise ValidationError(
                    node,
                    'The minimum bound must be lower than'
                    ' the maximum: %s < %s' % (min_value, max_value),
                )


class IntegerBoundConstraint(BoundConstraint):
    def __init__(self, *args, **kwargs):
        super(IntegerBoundConstraint, self).__init__(
            *args,
            schema_type=colander.Integer(),
            **kwargs
        )


class FieldType(colander.SchemaNode):
    def __init__(self, *args, **kwargs):
        kwargs['typ'] = OneOfType(
            colander.String,
            colander.Mapping(unknown='preserve'),
        )
        super(FieldType, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        if isinstance(cstruct, string_types):
            if cstruct not in TYPES_ALL \
                    and not RE_IDENTIFIER.match(cstruct):
                raise ValidationError(
                    node,
                    '"%r" is not a valid type identifier' % (cstruct,),
                )
        else:
            sub_schema(TypeDefinition, node, cstruct)


class Column(colander.SchemaNode):
    id = IdentifierString()  # pylint: disable=invalid-name
    description = Description()
    required = colander.SchemaNode(
        StrictBooleanType(),
        missing=colander.drop,
    )
    identifiable = colander.SchemaNode(
        StrictBooleanType(),
        missing=colander.drop,
    )

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Column, self).__init__(*args, **kwargs)
        self.add(FieldType(name='type'))


class ColumnCollection(colander.SequenceSchema):
    column = Column()

    def validator(self, node, cstruct):
        if len(cstruct) < 1:
            raise ValidationError(
                node,
                'Shorter than minimum length 1',
            )

        ids = [col['id'] for col in cstruct]
        duplicates = list(set([x for x in ids if ids.count(x) > 1]))
        if duplicates:
            raise ValidationError(
                node,
                'Column IDs must be unique within a collection:'
                ' %s' % ', '.join(duplicates),
            )


class Row(colander.SchemaNode):
    id = IdentifierString()  # pylint: disable=invalid-name
    description = Description()
    required = colander.SchemaNode(
        StrictBooleanType(),
        missing=colander.drop,
    )

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Row, self).__init__(*args, **kwargs)


class RowCollection(colander.SequenceSchema):
    row = Row()

    def validator(self, node, cstruct):
        if len(cstruct) < 1:
            raise ValidationError(
                node,
                'Shorter than minimum length 1',
            )

        ids = [row['id'] for row in cstruct]
        duplicates = list(set([x for x in ids if ids.count(x) > 1]))
        if duplicates:
            raise ValidationError(
                node,
                'Row IDs must be unique within a collection:'
                ' %s' % ', '.join(duplicates),
            )


class RangeConstraint(BoundConstraint):
    def __init__(self, *args, **kwargs):
        super(RangeConstraint, self).__init__(
            *args,
            **kwargs
        )


class TypeDefinition(colander.SchemaNode):
    base = colander.SchemaNode(colander.String())
    range = RangeConstraint(missing=colander.drop)
    length = IntegerBoundConstraint(missing=colander.drop)
    pattern = colander.SchemaNode(
        colander.String(),
        missing=colander.drop,
    )
    enumerations = EnumerationCollection(missing=colander.drop)
    columns = ColumnCollection(missing=colander.drop)
    rows = RowCollection(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(TypeDefinition, self).__init__(*args, **kwargs)
        self.add(Record(name='record', missing=colander.drop))


class RequiredOptionalField(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.OneOf([
        'required',
        'optional',
        'none',
    ])
    missing = colander.drop


class Field(colander.SchemaNode):
    id = IdentifierString()  # pylint: disable=invalid-name
    description = Description()
    type = FieldType()
    required = colander.SchemaNode(
        StrictBooleanType(),
        missing=colander.drop,
    )
    identifiable = colander.SchemaNode(
        StrictBooleanType(),
        missing=colander.drop,
    )
    annotation = RequiredOptionalField()
    explanation = RequiredOptionalField()

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Field, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        if 'annotation' in cstruct and cstruct['annotation'] != 'none':
            if 'required' in cstruct and cstruct['required']:
                raise ValidationError(
                    node,
                    'A Field cannot have an annotation'
                    ' if it is required: %s' % cstruct['id'],
                )


class Record(colander.SequenceSchema):
    field = Field()

    def validator(self, node, cstruct):
        if len(cstruct) < 1:
            raise ValidationError(
                node,
                'Shorter than minimum length 1',
            )

        ids = [field['id'] for field in cstruct]
        duplicates = list(set([x for x in ids if ids.count(x) > 1]))
        if duplicates:
            raise ValidationError(
                node,
                'Field IDs must be unique within a record:'
                ' %s' % ', '.join(duplicates),
            )


class InstrumentTypes(colander.SchemaNode):
    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='preserve')
        super(InstrumentTypes, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        cstruct = cstruct or {}
        for type_id, type_def in iteritems(cstruct):
            if type_id in TYPES_ALL or not RE_IDENTIFIER.match(type_id):
                raise ValidationError(
                    node,
                    '"%r" is not a valid custom type ID' % type_id,
                )
            sub_schema(TypeDefinition, node, type_def)


class Instrument(colander.SchemaNode):
    id = InstrumentIdentifier()  # pylint: disable=invalid-name
    version = Version()
    title = colander.SchemaNode(colander.String())
    description = Description()
    types = InstrumentTypes(missing=colander.drop)
    record = Record()
    meta = MetadataCollection(
        METADATA_PROPS,
        missing=colander.drop,
    )

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Instrument, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        for _, type_def in iteritems(cstruct.get('types', {})):
            self.check_type(type_def, node.get('types'), cstruct)
        for field in cstruct['record']:
            self.check_type(field['type'], node.get('record'), cstruct)

    def check_type(self, type_def, node, cstruct):
        try:
            full_type_def = get_full_type_definition(cstruct, type_def)
        except Exception as exc:
            raise ValidationError(
                node,
                str(exc),
            )

        self._check_required_constraints(full_type_def, node, type_def)
        self._check_appropriate_constraints(full_type_def, node)
        self._check_range_constraints(full_type_def, node)
        self._check_complex_subfields(full_type_def, node, cstruct)

        return full_type_def

    def _check_required_constraints(self, full_type_def, node, cstruct):
        if full_type_def['base'] in iterkeys(TYPES_CONSTRAINED_REQUIRED):
            for con in TYPES_CONSTRAINED_REQUIRED[full_type_def['base']]:
                if con not in full_type_def:
                    raise ValidationError(
                        node,
                        'Type definition "%r" missing required constraint'
                        ' "%s"' % (
                            cstruct,
                            con,
                        ),
                    )

    def _check_appropriate_constraints(self, full_type_def, node):
        for con in CONSTRAINTS_ALL:
            if con in full_type_def:
                if con not in TYPES_CONSTRAINED.get(full_type_def['base'], []):
                    raise ValidationError(
                        node,
                        'Constraint "%s" cannot be used on types based on'
                        ' "%s"' % (
                            con,
                            full_type_def['base'],
                        ),
                    )

    def _check_range_constraints(self, full_type_def, node):
        if 'range' in full_type_def \
                and full_type_def['base'] in RANGE_CONSTRAINT_TYPES:
            sub_schema(
                BoundConstraint(RANGE_CONSTRAINT_TYPES[full_type_def['base']]),
                node,
                full_type_def['range'],
            )

    def _check_complex_subfields(self, full_type_def, node, instrument):
        for sub_field_constraint in ('record', 'columns'):
            if sub_field_constraint in full_type_def:
                for field in full_type_def[sub_field_constraint]:
                    sub_type = self.check_type(field['type'], node, instrument)
                    if sub_type['base'] in TYPES_COMPLEX:
                        raise ValidationError(
                            node,
                            'Complex types cannot contain other complex'
                            ' types.',
                        )


def get_full_type_definition(instrument, type_def):
    """
    Returns a fully merged version of an Instrument Type Object that
    includes all constraints inherited from parent data types.

    The ``base`` property of this object will always reflect the base RIOS
    data type that the specified type definition is an implementation of.

    :param instrument:
        the full Instrument definition that the Field in question is a part of
    :type instrument: dict
    :param type_def:
        the contents of the ``type`` property from an Instrument Field
        definition
    :type type_def: dict or str
    :rtype: dict
    """

    if isinstance(type_def, string_types):
        if type_def in TYPES_ALL:
            return {
                'base': type_def
            }

        if type_def in iterkeys(instrument.get('types', {})):
            return get_full_type_definition(
                instrument,
                instrument['types'][type_def],
            )

        raise ValueError(
            'no type is defined for identifier "%s"' % (
                type_def,
            )
        )

    elif isinstance(type_def, dict):
        type_def = deepcopy(type_def)
        base_type = type_def.pop('base')

        try:
            parent_type_def = get_full_type_definition(instrument, base_type)
        except ValueError:
            raise ValueError(
                'invalid definition, references undefined base type "%s"' % (
                    base_type,
                )
            )

        parent_type_def.update(type_def)
        return parent_type_def

    else:
        raise TypeError(
            'type_def must be a string or dict, got "%r"' % (
                type_def,
            )
        )

