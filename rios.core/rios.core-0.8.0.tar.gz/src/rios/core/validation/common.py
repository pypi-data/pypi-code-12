#
# Copyright (c) 2015, Prometheus Research, LLC
#


import re

from collections import Callable
from contextlib import contextmanager

import colander

from six import iteritems


__all__ = (
    'RE_IDENTIFIER',
    'RE_PRODUCT_TOKENS',

    'ValidationError',
    'guard',
    'guard_sequence',

    'IdentifierString',
    'CompoundIdentifierString',
    'AnyType',
    'OneOfType',
    'StrictBooleanType',
    'OptionalStringType',
    'LanguageTag',
    'LocalizedMapping',
    'LocalizedString',
    'Options',
    'Descriptor',
    'DescriptorList',
    'MetadataCollection',

    'LocalizationChecker',
    'sub_schema',
    'validate_instrument_version',
)


# pylint: disable=abstract-method


BASE_IDENTIFIER_RESTR = r'[a-z](?:[a-z0-9]|[_](?![_]))*[a-z0-9]'
RE_IDENTIFIER = re.compile(r'^%s$' % BASE_IDENTIFIER_RESTR)
RE_COMPOUND_IDENTIFIER = re.compile(
    r'^%s(\.%s)*$' % (
        BASE_IDENTIFIER_RESTR,
        BASE_IDENTIFIER_RESTR,
    )
)

BASE_PRODUCT_RESTR = r'([^/\s]+)/([^/\s]+)'
RE_PRODUCT_TOKENS = re.compile(
    r'^(%s)(\s+%s)*$' % (
        BASE_PRODUCT_RESTR,
        BASE_PRODUCT_RESTR,
    )
)


ValidationError = colander.Invalid


@contextmanager
def guard(node, index=None):
    try:
        yield node
    except ValidationError as exc:
        new_exc = ValidationError(node)
        new_exc.add(exc, index)
        raise new_exc


@contextmanager
def guard_sequence(node, name, index):
    node = node.get(name + 's')
    with guard(node, index):
        subnode = node.get(name)
        with guard(subnode):
            yield subnode


class IdentifierString(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.Regex(RE_IDENTIFIER)


class CompoundIdentifierString(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.Regex(RE_COMPOUND_IDENTIFIER)


def sub_schema(schema, node, cstruct):
    if not isinstance(schema, colander.SchemaNode):
        schema = schema()
    try:
        schema.deserialize(cstruct)
    except ValidationError as exc:
        exc.node = node
        raise exc


class AnyType(colander.SchemaType):
    # pylint: disable=unused-argument
    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        return cstruct


class OneOfType(colander.SchemaType):
    def __init__(self, *args):
        self.possible_types = [
            arg() if isinstance(arg, Callable) else arg
            for arg in args
        ]

    def deserialize(self, node, cstruct):
        for i in range(len(self.possible_types)):
            try:
                return self.possible_types[i].deserialize(node, cstruct)
            except ValidationError:
                if i == (len(self.possible_types) - 1):
                    raise


class StrictBooleanType(colander.SchemaType):
    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null

        if isinstance(cstruct, bool):
            return cstruct

        raise ValidationError(
            node,
            '"%r" is not a boolean value' % (cstruct,)
        )


class OptionalStringType(colander.String):
    def deserialize(self, node, cstruct):
        if cstruct is colander.null or cstruct is None:
            return colander.null

        try:
            result = cstruct
            if isinstance(result, (colander.text_type, bytes)):
                if self.encoding:
                    result = colander.text_(cstruct, self.encoding)
                else:
                    result = colander.text_type(cstruct)
            else:
                raise ValidationError(node)
        except Exception as exc:
            raise ValidationError(
                node,
                colander._(
                    '${val} is not a string: ${err}',
                    mapping={
                        'val': cstruct,
                        'err': exc
                    }
                )
            )

        return result


RE_LANGUAGE_TAG = re.compile(
    r'^(((([A-Za-z]{2,3}(-([A-Za-z]{3}(-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})(-([A-Za-z]{4}))?(-([A-Za-z]{2}|[0-9]{3}))?(-([A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*(-([0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*(-(x(-[A-Za-z0-9]{1,8})+))?)|(x(-[A-Za-z0-9]{1,8})+)|((en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE)|(art-lojban|cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang)))$'  # noqa
)


class LanguageTag(colander.SchemaNode):
    schema_type = colander.String
    validator = colander.Regex(RE_LANGUAGE_TAG)


class LocalizedMapping(colander.SchemaNode):
    def __init__(self, sub_type, *args, **kwargs):
        self.sub_type = sub_type
        kwargs['typ'] = colander.Mapping(unknown='preserve')
        super(LocalizedMapping, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        cstruct = cstruct or {}

        if len(cstruct) == 0:
            raise ValidationError(
                node,
                'At least one localization must be specified',
            )

        for language_tag, translation in iteritems(cstruct):
            sub_schema(LanguageTag, node, language_tag)
            sub_schema(self.sub_type, node, translation)


class LocalizedString(LocalizedMapping):
    def __init__(self, *args, **kwargs):
        super(LocalizedString, self).__init__(
            colander.SchemaNode(colander.String()),
            *args,
            **kwargs
        )


class Options(colander.SchemaNode):
    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='preserve')
        super(Options, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        cstruct = cstruct or {}
        if len(cstruct) == 0:
            raise ValidationError(
                node,
                'At least one key/value pair must be defined',
            )


class Descriptor(colander.SchemaNode):
    id = colander.SchemaNode(colander.String())  # pylint: disable=invalid-name
    text = LocalizedString()
    help = LocalizedString(missing=colander.drop)

    def __init__(self, *args, **kwargs):
        kwargs['typ'] = colander.Mapping(unknown='raise')
        super(Descriptor, self).__init__(*args, **kwargs)


class DescriptorList(colander.SequenceSchema):
    descriptor = Descriptor()
    validator = colander.Length(min=1)


class MetadataCollection(colander.SchemaNode):
    def __init__(self, known_properties, *args, **kwargs):
        self.known_properties = known_properties
        kwargs['typ'] = colander.Mapping(unknown='preserve')
        super(MetadataCollection, self).__init__(*args, **kwargs)

    def validator(self, node, cstruct):
        cstruct = cstruct or {}
        if len(cstruct) == 0:
            raise ValidationError(
                node,
                'At least one property must be defined',
            )

        for prop, value in iteritems(cstruct):
            if prop in self.known_properties:
                sub_schema(self.known_properties[prop], node, value)


class LocalizationChecker(object):
    def __init__(self, node, default_localization):
        self.node = node
        self.locale = default_localization

    def ensure(self, obj, key, node=None, scope=None):
        if not isinstance(obj, dict) or key not in obj:
            return
        if self.locale not in obj[key]:
            raise ValidationError(
                node or self.node,
                '%sMissing default localization' % (
                    ('%s ' % scope) if scope else '',
                )
            )

    def ensure_descriptor(self, descriptor, scope=None):
        scope = scope or ''
        self.ensure(descriptor, 'text', scope=(scope + ' Text').strip())
        self.ensure(descriptor, 'help', scope=(scope + ' Help').strip())
        self.ensure(descriptor, 'audio', scope=(scope + ' Audio').strip())


def validate_instrument_version(instrument, obj, node):
    if instrument['id'] != obj['instrument']['id'] or \
            instrument['version'] != obj['instrument']['version']:
        raise ValidationError(
            node,
            'Incorrect Instrument version referenced',
        )

