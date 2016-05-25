import hug
from peewee import SqliteDatabase
import pytest

import hug_peewee_connect


api = hug.API(__name__)

@hug.get()
def fake_endpoint():
    return True


def test_manage_with_simple_url():
    db_instance = hug_peewee_connect.manage(api, 'sqlite://')
    model = db_instance.Model

    assert isinstance(db_instance, SqliteDatabase)
    assert db_instance.database == ':memory:'
    assert model._meta.database == db_instance
    assert hug.test.get(api, 'fake_endpoint').data == True


def test_manage_with_connection_params():
    db_instance = hug_peewee_connect.manage(api, 'sqlite://', port=5555)
    model = db_instance.Model

    assert isinstance(db_instance, SqliteDatabase)
    assert db_instance.connect_kwargs.get('port') == 5555
    assert db_instance.database == ':memory:'
    assert model._meta.database == db_instance

    with pytest.raises(TypeError):
        hug.test.get(api, 'fake_endpoint')
