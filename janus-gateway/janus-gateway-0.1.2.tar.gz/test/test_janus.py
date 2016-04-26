import threading

import janus


class EchoTestPlugin(janus.Plugin):

    name = 'janus.plugin.echotest'


def test_connection(janus_ws_url):

    opened_evt = threading.Event()
    closed_evt = threading.Event()

    def opened(cxn):
        opened_evt.set()

    def closed(cxn, code, reason):
        closed_evt.set()

    cxn = janus.Connection(janus_ws_url)
    cxn.on_opened.connect(opened, sender=cxn)

    cxn.on_closed.connect(closed, sender=cxn)
    cxn.cli.connect()

    opened_evt.wait(10)
    assert opened_evt.is_set

    cxn.cli.close()

    closed_evt.wait(10)
    assert closed_evt.is_set


def test_session_connection(janus_ws_url):
    session = janus.Session(janus_ws_url)
    echo = EchoTestPlugin()
    session.register_plugin(echo)
    assert len(session.plugins) == 1
    assert not session.plugins[0].is_attached

    f = session.connect()
    assert f.result(10) is session
    assert session.is_connected
    assert len(session.plugins) == 1

    f = session.create()
    assert f.result(10) is session
    assert session.is_created
    assert len(session.plugins) == 1
    assert session.plugins[0].is_attached
    assert session.plugin_idx == {
        session.plugins[0].id: session.plugins[0]
    }

    f = session.disconnect()
    assert f.result(10) is session
    assert not session.is_connected
    assert not session.is_created
    assert session.is_disconnected
    assert len(session.plugins) == 1
    assert not session.plugins[0].is_attached
    assert session.plugin_idx == {}


def test_event():
    e = janus.Event()

    assert not e.is_set()
    assert not e.isSet()
    assert not e.wait(0)

    assert not e.clear()
    assert not e.is_set()
    assert not e.isSet()
    assert not e.wait(0)

    assert not e.set()
    assert e.is_set()
    assert e.isSet()
    assert e.wait(0)

    assert not e.clear()
    assert not e.is_set()
    assert not e.isSet()
    assert not e.wait(0)
