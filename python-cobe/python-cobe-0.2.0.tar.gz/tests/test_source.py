import pathlib
import unittest.mock
import time

import msgpack
import pytest
import voluptuous
import zmq

import cobe
import cobe.model
import cobe.source
import cobe.testing


UEID_FOO = '716eec5f78bfa9b97ff69ccda90c7f7a'
UEID_BAR = '31f596aa85f36577720cf361cd8715d1'


class TestSchemaNumber:

    def test_int(self):
        assert cobe.source._SCHEMA_NUMBER(0) == 0

    def test_float(self):
        assert cobe.source._SCHEMA_NUMBER(0.0) == 0.0

    def test_wrong_type(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_NUMBER(object())


class TestSchemaPrimitive:

    def test_nil(self):
        assert cobe.source._SCHEMA_PRIMITIVE(None) is None

    @pytest.mark.parametrize('value', [0, 0.0])
    def test_number(self, value):
        assert cobe.source._SCHEMA_PRIMITIVE(value) == value

    def test_unicode(self):
        assert cobe.source._SCHEMA_PRIMITIVE('') == ''

    def test_bytes(self):
        assert cobe.source._SCHEMA_PRIMITIVE(b'') == b''

    def test_ueid(self):
        assert cobe.source._SCHEMA_PRIMITIVE(cobe.UEID('a' * 32)) == 'a' * 32

    def test_wrong_type(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_NUMBER(object())


class TestSchemaComposite:

    def test_array(self):
        assert cobe.source._SCHEMA_COMPOSITE([
            None,
            0,
            0.0,
            '',
            b'',
            cobe.UEID('a' * 32),
        ]) == [
            None,
            0,
            0.0,
            '',
            b'',
            'a' * 32,
        ]

    def test_array_empty(self):
        assert cobe.source._SCHEMA_COMPOSITE([]) == []

    def test_array_wrong_type_element(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_COMPOSITE([object()])

    def test_array_nested_array(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_COMPOSITE([[]])

    def test_array_nested_mapping(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_COMPOSITE([{}])

    def test_mapping(self):
        assert cobe.source._SCHEMA_COMPOSITE({
            'nil': None,
            'number-int': 0,
            'number-float': 0.0,
            'unicode': '',
            'bytes': b'',
            'ueid': cobe.UEID('a' * 32),
        }) == {
            'nil': None,
            'number-int': 0,
            'number-float': 0.0,
            'unicode': '',
            'bytes': b'',
            'ueid': 'a' * 32,
        }

    def test_mapping_empty(self):
        assert cobe.source._SCHEMA_COMPOSITE({}) == {}

    def test_mapping_wrong_type_key(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_COMPOSITE({object(): ''})

    def test_mapping_wrong_type_value(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_COMPOSITE({'': object()})

    def test_mapping_nested_array(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_COMPOSITE({'': []})

    def test_mapping_nested_mapping(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_COMPOSITE({'': {}})


class TestSchemaPrintable:

    def test(self):
        assert cobe.source._SCHEMA_PRINTABLE('Катюша') == 'Катюша'

    def test_separator(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_PRINTABLE(' ')

    def test_control(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_PRINTABLE('\n')

    def test_solidus(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_PRINTABLE('/')


class TestSchemaTraits:

    def test(self):
        validated = cobe.source._SCHEMA_TRAITS({'foo', 'bar'})
        assert isinstance(validated, list)
        assert sorted(validated) == sorted(['foo', 'bar'])

    def test_wrong_type(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_TRAITS(object())

    def test_wrong_type_inner(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_TRAITS({object()})

    def test_not_printable(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_TRAITS({'\n'})


class TestSchemaIdentifiable:

    def test_identifier(self):
        identifier = cobe.model.Identifier('Foo')
        assert cobe.source._SCHEMA_IDENTIFIABLE(identifier) == UEID_FOO

    def test_update(self):
        update = cobe.model.Update('Foo')
        assert cobe.source._SCHEMA_IDENTIFIABLE(update) == UEID_FOO

    def test_wrong_type(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_IDENTIFIABLE(object())

    def test_bad_ueid_provider(self, monkeypatch):
        mock = unittest.mock.Mock(return_value=object())
        monkeypatch.setattr(cobe.model.Identifier, 'ueid', mock)
        identifier = cobe.model.Identifier('Foo')
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_IDENTIFIABLE(identifier)


class TestSchemaAttribute:

    @pytest.mark.parametrize(('value', 'expected'), [
        (None, None),
        (0, 0),
        (0.0, 0.0),
        ('', ''),
        (b'', b''),
        (cobe.UEID('a' * 32), 'a' * 32),
        ([], []),
        ({}, {}),
    ])
    def test_set(self, value, expected):
        attribute = cobe.model.Attribute()
        attribute.set(value)
        attribute.traits.add('foo')
        attribute.traits.add('bar')
        validated = cobe.source._SCHEMA_ATTRIBUTE(attribute)
        traits = validated.pop('traits')
        assert validated == {
            'value': expected,
            'deleted': False,
        }
        assert sorted(traits) == ['bar', 'foo']

    def test_set_value_wrong_type(self):
        attribute = cobe.model.Attribute()
        attribute.set(object())
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_ATTRIBUTE(attribute)

    def test_set_traits_wrong_type(self):
        attribute = cobe.model.Attribute()
        attribute.set(None)
        attribute.traits = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_ATTRIBUTE(attribute)

    def test_set_traits_wrong_type_inner(self):
        attribute = cobe.model.Attribute()
        attribute.set(None)
        attribute.traits.add(object())
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_ATTRIBUTE(attribute)

    def test_set_traits_not_printable(self):
        attribute = cobe.model.Attribute()
        attribute.set(None)
        attribute.traits.add('\n')
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_ATTRIBUTE(attribute)

    def test_delete(self):
        attribute = cobe.model.Attribute()
        attribute.delete()
        assert cobe.source._SCHEMA_ATTRIBUTE(attribute) == {'deleted': True}

    def test_not_set(self):
        attribute = cobe.model.Attribute()
        attribute.unset()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_ATTRIBUTE(attribute)


class TestSchemaAttributes:

    def test(self):
        attributes = cobe.model.Attributes()
        attributes['foo'].set(None)
        attributes['bar'].delete()
        assert cobe.source._SCHEMA_ATTRIBUTES(attributes) == {
            'foo': {
                'value': None,
                'traits': [],
                'deleted': False,
            },
            'bar': {
                'deleted': True,
            },
        }

    def test_wrong_type(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_ATTRIBUTES(object())

    def test_skip_not_set(self):
        attributes = cobe.model.Attributes()
        attributes['foo'].unset()
        attributes['bar'].unset()
        assert cobe.source._SCHEMA_ATTRIBUTES(attributes) == {}


class TestSchemaRelationships:

    def test(self):
        validated = cobe.source._SCHEMA_RELATIONSHIPS((
            cobe.UEID('a' * 32),
            cobe.model.Identifier('Foo'),
            cobe.model.Update('Bar'),
        ))
        assert isinstance(validated, list)
        assert sorted(validated) == [UEID_BAR, UEID_FOO, 'a' * 32]

    def test_wrong_type(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_RELATIONSHIPS(object())

    def test_wrong_type_inner(self):
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_RELATIONSHIPS({object()})

    def test_bad_ueid_provider(self, monkeypatch):
        mock = unittest.mock.Mock(return_value=object())
        monkeypatch.setattr(cobe.model.Identifier, 'ueid', mock)
        identifier = cobe.model.Identifier('Foo')
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_RELATIONSHIPS((cobe.model.Identifier('Foo'),))


class TestSchemaUpdate:

    @pytest.fixture()
    def update(self):
        return {
            'ueid': cobe.model.Update('Foo'),
            'timestamp': 1234.0,
            'exists': True,
            'type': 'Foo',
            'ttl': 60,
            'label': '...',
            'attrs': cobe.model.Attributes(),
            'parents': (),
            'children': (),
        }

    def test(self, update):
        assert cobe.source._SCHEMA_UPDATE(update) == {
            'ueid': UEID_FOO,
            'timestamp': 1234.0,
            'exists': True,
            'type': 'Foo',
            'ttl': 60,
            'label': '...',
            'attrs': {},
            'parents': [],
            'children': [],
        }

    def test_ueid_wrong_type(self, update):
        update['ueid'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_ueid_missing(self, update):
        del update['ueid']
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_ueid_error(self, monkeypatch, update):
        monkeypatch.setattr(
            update['ueid'],
            'ueid',
            unittest.mock.Mock(side_effect=cobe.UEIDError),
        )
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_timestamp_int(self, update):
        update['timestamp'] = 1234
        validated = cobe.source._SCHEMA_UPDATE(update)
        assert validated['timestamp'] == 1234

    def test_timestamp_float(self, update):
        update['timestamp'] = 1234.0
        validated = cobe.source._SCHEMA_UPDATE(update)
        assert validated['timestamp'] == 1234.0

    def test_timestamp_wrong_type(self, update):
        update['timestamp'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_timestamp_missing(self, update):
        del update['timestamp']
        validated = cobe.source._SCHEMA_UPDATE(update)
        assert 'timestamp' not in validated

    def test_exists_wrong_type(self, update):
        update['exists'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_exists_missing(self, update):
        del update['exists']
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_type_wrong_type(self, update):
        update['type'] = object()
        with pytest.raises(voluptuous.Invalid) as exc:
            cobe.source._SCHEMA_UPDATE(update)

    def test_type_missing(self, update):
        del update['type']
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_type_not_printable(self, update):
        update['type'] = '\n'
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_ttl_int(self, update):
        update['ttl'] = 420
        validated = cobe.source._SCHEMA_UPDATE(update)
        assert validated['ttl'] == 420

    def test_ttl_float(self, update):
        update['ttl'] = 420.0
        validated = cobe.source._SCHEMA_UPDATE(update)
        assert validated['ttl'] == 420.0

    def test_ttl_wrong_type(self, update):
        update['ttl'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_ttl_missing(self, update):
        del update['ttl']
        validated = cobe.source._SCHEMA_UPDATE(update)
        assert 'ttl' not in validated

    def test_label_wrong_type(self, update):
        update['label'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_label_missing(self, update):
        del update['label']
        validated = cobe.source._SCHEMA_UPDATE(update)
        assert 'label' not in validated

    def test_attrs_wrong_type(self, update):
        update['attrs'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_attrs_missing(self, update):
        del update['attrs']
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_parents_wrong_type(self, update):
        update['parents'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_parents_missing(self, update):
        del update['parents']
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_children_wrong_type(self, update):
        update['children'] = object()
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)

    def test_children_missing(self, update):
        del update['children']
        with pytest.raises(voluptuous.Invalid):
            cobe.source._SCHEMA_UPDATE(update)


class TestToken:

    @pytest.fixture()
    def key_source_public(self):
        return b'SPubSPubSPubSPubSPubSPubSPubSPubSPubSPub'

    @pytest.fixture()
    def key_source_private(self):
        return b'SPriSPriSPriSPriSPriSPriSPriSPriSPriSPri'

    @pytest.fixture()
    def key_receiver_public(self):
        return b'RPubRPubRPubRPubRPubRPubRPubRPubRPubRPub'

    @pytest.fixture()
    def key_source(self, directory, key_source_public, key_source_private):
        location = directory / 'source.key'
        with location.open('w') as key:
            key.write("""\
            #   ****  Generated on 2016-05-12 14:54:29.358150 by pyzmq  ****

            metadata
            curve
                public-key = "{}"
                secret-key = "{}"
            """.format(
                key_source_public.decode(),
                key_source_private.decode(),
            ))
        return location

    @pytest.fixture()
    def key_receiver(self, directory, key_receiver_public):
        location = directory / 'receiver.key'
        with location.open('w') as key:
            key.write("""\
            #   ****  Generated on 2016-05-12 14:54:29.358150 by pyzmq  ****

            metadata
            curve
                public-key = "{}"
            """.format(key_receiver_public.decode()))
        return location

    def test_authenticate(
            self, key_source_public, key_source_private, key_receiver_public):
        # Can't read CURVE_ options from a real socket
        socket = unittest.mock.Mock()
        token = cobe.Token(
            key_source_public,
            key_source_private,
            key_receiver_public,
        )
        token.authenticate(socket)
        assert (socket.CURVE_PUBLICKEY == key_source_public)
        assert (socket.CURVE_SECRETKEY == key_source_private)
        assert (socket.CURVE_SERVERKEY == key_receiver_public)

    @pytest.mark.parametrize('path', [str, pathlib.Path])
    def test_from_key_files(
            self, key_source_public, key_source_private,
            key_receiver_public, key_source, key_receiver, path):
        token = cobe.Token.from_key_files(path(key_source), path(key_receiver))
        socket = unittest.mock.Mock()
        token.authenticate(socket)
        assert socket.CURVE_PUBLICKEY == key_source_public
        assert socket.CURVE_SECRETKEY == key_source_private
        assert socket.CURVE_SERVERKEY == key_receiver_public

    def test_from_key_files_source_no_public_key(
            self, key_source, key_receiver):
        with key_source.open('r') as key:
            lines = []
            for line in key:
                if 'public-key' not in line:
                    lines.append(line)
        with key_source.open('w') as key:
            key.write('\n'.join(lines))
        with pytest.raises(cobe.TokenError) as exc:
            cobe.Token.from_key_files(key_source, key_receiver)
        assert 'Source' in str(exc.value)
        assert 'missing a public key' in str(exc.value)

    def test_from_key_files_source_no_private_key(
            self, key_source, key_receiver):
        with key_source.open('r') as key:
            lines = []
            for line in key:
                if 'secret-key' not in line:
                    lines.append(line)
        with key_source.open('w') as key:
            key.write('\n'.join(lines))
        with pytest.raises(cobe.TokenError) as exc:
            cobe.Token.from_key_files(key_source, key_receiver)
        assert 'Source' in str(exc.value)
        assert 'missing a private key' in str(exc.value)

    def test_from_key_files_receiver_no_public_key(
            self, key_source, key_receiver):
        with key_receiver.open('r') as key:
            lines = []
            for line in key:
                if 'public-key' not in line:
                    lines.append(line)
        with key_receiver.open('w') as key:
            key.write('\n'.join(lines))
        with pytest.raises(cobe.TokenError) as exc:
            cobe.Token.from_key_files(key_source, key_receiver)
        assert 'Receiver' in str(exc.value)
        assert 'missing a public key' in str(exc.value)

    def test_from_key_files_receiver_has_private_key(
            self, key_source, key_receiver):
        with key_receiver.open('a') as key:
            key.write(
                '    secret-key = "RPriRPriRPriRPriRPriRPriRPriRPriRPriRPri"')
        with pytest.warns(UserWarning) as warning:
            cobe.Token.from_key_files(key_source, key_receiver)
        assert 'Receiver' in str(warning[0].message)
        assert 'contained a private key' in str(warning[0].message)


class TestSource:

    @pytest.yield_fixture()
    def token(self):
        with cobe.testing.Receiver() as receiver:
            yield receiver.token

    @pytest.yield_fixture()
    def source(self, token):
        source = cobe.Source(destination='tcp://localhost:9001', token=token)
        yield source
        source.close()

    @pytest.fixture(params=[
        '127.0.0.1',
        'localhost',
        '[::1]',
        '[::ffff:127.0.0.1]',
    ])
    def destination(self, request):
        return request.param

    def test_context_manager(self, source):
        assert source._opened is False
        assert source._closed is False
        with source:
            assert source._opened is True
            assert source._closed is False
        assert source._opened is False
        assert source._closed is True

    def test_context_manager_after_open(self, source):
        source.open()
        with pytest.raises(cobe.SourceError):
            with source:
                pass

    def test_context_manager_after_close(self, source):
        source.open()
        source.close()
        with pytest.raises(cobe.SourceError):
            with source:
                pass

    def test_context_manager_after_close_immediate(self, source):
        source.close()
        with pytest.raises(cobe.SourceError):
            with source:
                pass

    def test_open_after_open(self, source):
        source.open()
        with pytest.raises(cobe.SourceError):
            source.open()

    def test_open_after_close(self, source):
        source.open()
        source.close()
        with pytest.raises(cobe.SourceError):
            source.open()

    def test_open_after_close_immediate(self, source):
        source.close()
        with pytest.raises(cobe.SourceError):
            source.open()

    def test_close_before_open(self, source):
        source.close()  # Should not raise

    def test_close_after_open(self, source):
        # Normative test; effectively same as test_context_manager
        source.open()
        source.close()

    def test_close_after_close(self, source):
        source.open()
        source.close()
        source.close()  # Should not raise

    def test_send_before_open(self, source):
        with pytest.raises(cobe.SourceError):
            source.send(cobe.Model())

    def test_send_after_close(self, source):
        source.open()
        source.close()
        with pytest.raises(cobe.SourceError):
            source.send(cobe.Model())

    def test_send_after_close_immediate(self, source):
        source.close()
        with pytest.raises(cobe.SourceError):
            source.send(cobe.Model())

    def test_destination_no_scheme(self, token, destination):
        source = cobe.Source(
            destination='//{}:9001'.format(destination), token=token)
        assert source.destination == 'tcp://{}:9001'.format(destination)

    def test_destination_no_scheme_or_slashes(self, token, destination):
        source = cobe.Source(
            destination='{}:9001'.format(destination), token=token)
        assert source.destination == 'tcp://{}:9001'.format(destination)

    def test_destination_no_port(self, token, destination):
        source = cobe.Source(
            destination='tcp://{}'.format(destination), token=token)
        assert source.destination == 'tcp://{}:25010'.format(destination)

    def test_destination_no_scheme_no_port(self, token, destination):
        source = cobe.Source(
            destination='//{}'.format(destination), token=token)
        assert source.destination == 'tcp://{}:25010'.format(destination)

    def test_destination_authority_only(self, token, destination):
        source = cobe.Source(destination=destination, token=token)
        assert source.destination == 'tcp://{}:25010'.format(destination)

    def test_destination_scheme_only(self, token):
        with pytest.raises(cobe.SourceError):
            cobe.Source(destination='tcp://', token=token)

    def test_destination_scheme_wrong(self, token):
        with pytest.raises(cobe.SourceError):
            cobe.Source(destination='ipc://', token=token)

    def test_destination_port_only(self, token):
        with pytest.raises(cobe.SourceError):
            cobe.Source(destination='tcp://:9001', token=token)

    def test_destination_port_and_path_only(self, token):
        with pytest.raises(cobe.SourceError):
            cobe.Source(destination='tcp://:9001/foo/bar', token=token)

    def test_destination_port_not_numeric(self, token, destination):
        with pytest.raises(cobe.SourceError):
            cobe.Source(
                destination='tcp://{}:asdf'.format(destination), token=token)

    def test_destination_tcp_with_path(self, token, destination):
        with pytest.raises(cobe.SourceError):
            cobe.Source(
                destination='tcp://{}:9001/foo/bar'.format(destination),
                token=token,
            )

    def test_destination_empty(self, token):
        with pytest.raises(cobe.SourceError):
            cobe.Source(destination='', token=token)


class TestSourceSend:

    @pytest.yield_fixture()
    def receiver(self):
        with cobe.testing.Receiver() as receiver:
            yield receiver

    @pytest.fixture()
    def source(self, receiver):
        """An un-opened entity source.

        The source is configured to send updates to the receiver managed
        by the fixture of the same name.

        :returns: A :class:`cobe.Source` object.
        """
        return cobe.Source(
            destination=receiver.destination, token=receiver.token)

    def test(self, receiver, source):
        model = cobe.Model()
        update_1 = cobe.Update('Foo')
        update_1.attributes['spam'].set('eggs')
        update_1.attributes['spam'].traits.add('traitor')
        update_2 = cobe.Update('Bar')
        update_2.attributes['spam'].set('eggs')
        update_2.attributes['spam'].traits.add('traitor')
        model.relate(parent=update_1, child=update_2)
        with source:
            source.send(model)
        print(receiver._authenticator.thread.authenticator.certs)
        message_1, message_2 = receiver.expect_raw(2)
        assert message_1[0] == b'streamapi/4'
        assert msgpack.unpackb(message_1[1], encoding='utf-8') == {
            'ueid': UEID_FOO,
            'type': 'Foo',
            'exists': True,
            'parents': [],
            'children': [UEID_BAR],
            'attrs': {
                'spam': {
                    'value': 'eggs',
                    'traits': ['traitor'],
                    'deleted': False,
                },
            },
        }
        assert message_2[0] == b'streamapi/4'
        assert msgpack.unpackb(message_2[1], encoding='utf-8') == {
            'ueid': UEID_BAR,
            'type': 'Bar',
            'exists': True,
            'parents': [UEID_FOO],
            'children': [],
            'attrs': {
                'spam': {
                    'value': 'eggs',
                    'traits': ['traitor'],
                    'deleted': False,
                },
            },
        }

    @pytest.mark.parametrize(('timestamp', 'type_'), [
        (123, int),
        (123.0, float),
    ])
    def test_timestamp(self, receiver, source, timestamp, type_):
        model = cobe.Model()
        update = cobe.Update('Foo')
        update.timestamp = timestamp
        model.add(update)
        with source:
            source.send(model)
        message = receiver.expect_raw(1)[0]
        update_encoded = msgpack.unpackb(message[1], encoding='utf-8')
        assert message[0] == b'streamapi/4'
        assert update_encoded == {
            'ueid': UEID_FOO,
            'type': 'Foo',
            'exists': True,
            'parents': [],
            'children': [],
            'attrs': {},
            'timestamp': timestamp,
        }
        assert isinstance(update_encoded['timestamp'], type_)

    def test_label(self, receiver, source):
        model = cobe.Model()
        update = cobe.Update('Foo')
        update.label = 'bar'
        model.add(update)
        with source:
            source.send(model)
        message = receiver.expect_raw(1)[0]
        update_encoded = msgpack.unpackb(message[1], encoding='utf-8')
        assert message[0] == b'streamapi/4'
        assert update_encoded == {
            'ueid': UEID_FOO,
            'type': 'Foo',
            'exists': True,
            'parents': [],
            'children': [],
            'attrs': {},
            'label': 'bar',
        }

    @pytest.mark.parametrize(('ttl', 'type_'), [
        (123, int),
        (123.0, float),
    ])
    def test_ttl(self, receiver, source, ttl, type_):
        model = cobe.Model()
        update = cobe.Update('Foo')
        update.ttl = ttl
        model.add(update)
        with source:
            source.send(model)
        message = receiver.expect_raw(1)[0]
        update_encoded = msgpack.unpackb(message[1], encoding='utf-8')
        assert message[0] == b'streamapi/4'
        assert update_encoded == {
            'ueid': UEID_FOO,
            'type': 'Foo',
            'exists': True,
            'parents': [],
            'children': [],
            'attrs': {},
            'ttl': ttl,
        }
        assert isinstance(update_encoded['ttl'], type_)

    @pytest.mark.parametrize('attribute', [
        'type',
        'exists',
        'timestamp',
        'ttl',
    ])
    def test_invalid_update(self, receiver, source, attribute):
        model = cobe.Model()
        update = cobe.Update('Foo')
        setattr(update, attribute, object())
        model.add(update)
        with source:
            with pytest.raises(cobe.ProtocolError):
                source.send(model)

    def test_bad_destination(self, receiver, source):
        receiver.close()
        model = cobe.Model()
        model.add(cobe.Update('Foo'))  # One message per model
        with source:
            with pytest.raises(cobe.SourceError):
                for _ in range(source._socket.get_hwm() + 1):
                    source.send(model)

    @pytest.mark.parametrize('attribute', ('_public', '_private', '_receiver'))
    def test_bad_token(self, receiver, source, attribute):
        model = cobe.Model()
        model.add(cobe.Update('Foo'))  # One message per model
        setattr(source._token,
                attribute, b'~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        with source:
            with pytest.raises(cobe.SourceError):
                for _ in range(source._socket.get_hwm() + 1):
                    source.send(model)

    def test_unserialisable(self, monkeypatch, source):
        bad_schema = unittest.mock.Mock(return_value=object())
        monkeypatch.setattr(cobe.source, '_SCHEMA_UPDATE', bad_schema)
        model = cobe.Model()
        model.add(cobe.Update('Foo'))
        with source:
            with pytest.raises(cobe.ProtocolError):
                source.send(model)
