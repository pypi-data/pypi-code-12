import hug
import hug_peewee_connect
import pytest
from peewee import SqliteDatabase

api = hug.API(__name__)


@hug.get()
def fake_endpoint():
    return True


@hug.get()
def skip_me():
    return True


def test_manage_with_simple_url():
    db_instance = hug_peewee_connect.manage(api, 'sqlite://')
    model = db_instance.Model

    assert isinstance(db_instance, SqliteDatabase)
    assert db_instance.database == ':memory:'
    assert model._meta.database == db_instance
    assert hug.test.get(api, 'fake_endpoint').data is True


def test_manage_without_exclude():
    db_instance = hug_peewee_connect.manage(api, 'sqlite://')
    model = db_instance.Model
    call_stack = _patch(db_instance)

    assert hug.test.get(api, 'skip_me').data is True
    assert call_stack.pop() == 'close'
    assert call_stack.pop() == 'connect'


def test_manage_with_exclude():
    def exclude(request, _):
        return request.path == 'skip_me'

    db_instance = hug_peewee_connect.manage(api, 'sqlite://', exclude=exclude)
    model = db_instance.Model
    call_stack = _patch(db_instance)

    assert hug.test.get(api, 'skip_me').data is True
    assert call_stack == []


def test_manage_with_connection_params():
    db_instance = hug_peewee_connect.manage(api, 'sqlite://', port=5555)
    model = db_instance.Model

    assert isinstance(db_instance, SqliteDatabase)
    assert db_instance.connect_kwargs.get('port') == 5555
    assert db_instance.database == ':memory:'
    assert model._meta.database == db_instance

    with pytest.raises(TypeError):
        hug.test.get(api, 'fake_endpoint')


def _patch(db_instance):
    stack = []

    def patch_connect():
        stack.append('connect')

    def patch_close():
        stack.append('close')

    db_instance.connect = patch_connect
    db_instance.close = patch_close

    return stack
