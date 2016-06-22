import unittest.mock

import pytest
import zmq
import zmq.auth.thread

import cobe
import cobe.testing


class TestTimeoutError:

    def test(self):
        exception = cobe.testing.TimeoutError(5, [1, 2, 3], 2.5)
        assert exception.count_expected == 5
        assert exception.count_received == 3
        assert exception.partial == [1, 2, 3]
        assert exception.elapsed == 2.5

    def test_str(self):
        exception = cobe.testing.TimeoutError(5, [1, 2, 3], 2.5)
        assert str(exception) == 'Expected 5 but received 3 in 2.50 seconds'


class TestReceiver:

    def test_context_manager(self):
        with cobe.testing.Receiver() as receiver:
            assert receiver._closed is False
        assert receiver._closed is True

    def test_enter_whilst_closed(self):
        receiver = cobe.testing.Receiver()
        receiver.close()
        with pytest.raises(cobe.testing.ReceiverError):
            receiver.__enter__()

    def test_exit_whilst_closed(self):
        receiver = cobe.testing.Receiver()
        receiver.close()
        receiver.__exit__(..., ..., ...)

    def test_close_whilst_closed(self):
        receiver = cobe.testing.Receiver()
        receiver.close()
        receiver.close()  # Should not raise

    def test_bind_address_in_use(self, monkeypatch):
        mock_authenticator = unittest.mock.MagicMock()
        monkeypatch.setattr(
            zmq.auth.thread, 'ThreadAuthenticator', mock_authenticator)
        mock_bind = unittest.mock.Mock(
            side_effect=zmq.ZMQError(zmq.EADDRINUSE))
        monkeypatch.setattr(zmq.Socket, 'bind', mock_bind)
        with pytest.raises(cobe.testing.ReceiverError):
            with cobe.testing.Receiver():
                pass

    def test_bind_other_error(self, monkeypatch):
        mock_authenticator = unittest.mock.MagicMock()
        monkeypatch.setattr(
            zmq.auth.thread, 'ThreadAuthenticator', mock_authenticator)
        mock_bind = unittest.mock.Mock(
            side_effect=zmq.ZMQError(zmq.ENOTSOCK))
        monkeypatch.setattr(zmq.Socket, 'bind', mock_bind)
        with pytest.raises(cobe.testing.ReceiverError) as exc:
            with cobe.testing.Receiver():
                pass
        assert str(exc.value) == str(exc.value.__context__)
        assert exc.value.__context__.errno == zmq.ENOTSOCK

    def test_destination(self):
        with cobe.testing.Receiver() as receiver:
            scheme, authority_and_port = receiver.destination.split(':', 1)
            authority, port = authority_and_port.rsplit(':', 1)
            assert scheme == 'tcp'
            assert authority == '//[::ffff:127.0.0.1]'
            assert int(port) > 1
            assert int(port) < 65536

    def test_destination_before_open(self):
        receiver = cobe.testing.Receiver()
        with pytest.raises(cobe.testing.ReceiverError):
            assert receiver.destination

    def test_destination_whilst_closed(self):
        receiver = cobe.testing.Receiver()
        receiver.close()
        with pytest.raises(cobe.testing.ReceiverError):
            assert receiver.destination

    def test_token(self):
        with cobe.testing.Receiver() as receiver:
            assert isinstance(receiver.token, cobe.Token)

    def test_token_before_open(self):
        receiver = cobe.testing.Receiver()
        with pytest.raises(cobe.testing.ReceiverError):
            assert receiver.token

    def test_token_whilst_closed(self):
        receiver = cobe.testing.Receiver()
        receiver.close()
        with pytest.raises(cobe.testing.ReceiverError):
            assert receiver.token


class TestReceiverExpectRaw:

    @pytest.yield_fixture()
    def receiver(self):
        with cobe.testing.Receiver() as receiver:
            yield receiver

    @pytest.yield_fixture()
    def socket(self, receiver):
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        receiver.token.authenticate(socket)
        socket.connect(receiver.destination)
        yield socket
        socket.close()
        context.term()

    def test(self, receiver, socket):
        socket.send_multipart((b'foo', b'bar'))
        socket.send_multipart((b'spam', b'eggs'))
        messages = receiver.expect_raw(2)
        assert messages == (
            (b'foo', b'bar'),
            (b'spam', b'eggs'),
        )

    def test_timeout(self, receiver):
        with pytest.raises(cobe.testing.TimeoutError) as exc:
            receiver.expect_raw()
        assert exc.value.count_expected == 1
        assert exc.value.count_received == 0
        assert exc.value.partial == ()
        assert exc.value.elapsed >= 1.0

    def test_partial(self, receiver, socket):
        socket.send(b'foo')
        socket.send(b'bar')
        with pytest.raises(cobe.testing.TimeoutError) as exc:
            receiver.expect_raw(3, 1.5)
        assert exc.value.count_expected == 3
        assert exc.value.count_received == 2
        assert exc.value.partial == ((b'foo',), (b'bar',))
        assert exc.value.elapsed >= 1.5


class TestReceiverExpect:

    @pytest.yield_fixture()
    def receiver(self):
        with cobe.testing.Receiver() as receiver:
            yield receiver

    @pytest.yield_fixture()
    def source(self, receiver):
        source = cobe.Source(
            destination=receiver.destination, token=receiver.token)
        with source:
            yield source

    def test(self, receiver, source):
        model = cobe.Model()
        update_1 = cobe.Update('Foo')
        update_1.label = 'foo'
        update_1.timestamp = 123
        update_1.ttl = 60
        update_2 = cobe.Update('Bar')
        update_2.attributes['qux'].delete()
        update_2.attributes['spam'].set('eggs')
        update_2.attributes['spam'].traits.add('traitor')
        model.relate(parent=update_1, child=update_2)
        source.send(model)
        received_model = receiver.expect(2)
        (received_1_update,
         received_1_parents,
         received_1_children) = list(received_model)[0]
        (received_2_update,
         received_2_parents,
         received_2_children) = list(received_model)[1]
        assert len(received_model) == 2
        assert received_1_update.type == 'Foo'
        assert received_1_update.label == 'foo'
        assert received_1_update.timestamp == 123
        assert received_1_update.ttl == 60
        assert received_1_update == update_1
        assert received_1_parents == ()
        assert received_1_children == (received_2_update,)
        assert received_2_update.type == 'Bar'
        assert received_2_update.attributes['qux'].is_deleted()
        assert received_2_update.attributes['spam'].value == 'eggs'
        assert received_2_update.attributes['spam'].traits == {'traitor'}
        assert received_2_update == update_2
        assert received_2_parents == (received_1_update,)
        assert received_2_children == ()

    def test_identifier(self, receiver, source):
        # Identifiers become UEIDs in reconstructed models
        model = cobe.Model()
        update = cobe.Update('Foo')
        parent_identifier = cobe.Identifier('Bar')
        child_identifier = cobe.Identifier('Baz')
        model.relate(parent=parent_identifier, child=update)
        model.relate(parent=update, child=child_identifier)
        source.send(model)
        received_model = receiver.expect(1)
        (received_update,
         received_parents,
         received_children) = list(received_model)[0]
        assert len(received_model) == 1
        assert received_update == update
        assert received_parents == (parent_identifier,)
        assert received_children == (child_identifier,)
        assert isinstance(received_parents[0], cobe.UEID)
        assert isinstance(received_children[0], cobe.UEID)

    def test_timeout(self, receiver):
        with pytest.raises(cobe.testing.TimeoutError) as exc:
            receiver.expect()
        assert exc.value.count_expected == 1
        assert exc.value.count_received == 0
        assert isinstance(exc.value.partial, cobe.Model)
        assert list(exc.value.partial) == []
        assert exc.value.elapsed >= 1.0

    def test_partial(self, receiver, source):
        model = cobe.Model()
        update_1 = cobe.Update('Foo')
        update_2 = cobe.Update('Bar')
        model.add(update_1)
        model.add(update_2)
        source.send(model)
        with pytest.raises(cobe.testing.TimeoutError) as exc:
            receiver.expect(3, 1.5)
        assert exc.value.count_expected == 3
        assert exc.value.count_received == 2
        assert isinstance(exc.value.partial, cobe.Model)
        assert list(exc.value.partial)[0][0] == update_1
        assert list(exc.value.partial)[0][1] == ()
        assert list(exc.value.partial)[0][2] == ()
        assert list(exc.value.partial)[1][0] ==  update_2
        assert list(exc.value.partial)[1][1] == ()
        assert list(exc.value.partial)[1][2] == ()
        assert exc.value.elapsed >= 1.5
