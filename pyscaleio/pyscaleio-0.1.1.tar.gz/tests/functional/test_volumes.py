from __future__ import unicode_literals

import pytest

from pyscaleio import System, StoragePool, Volume, Sdc
from pyscaleio import exceptions
from pyscaleio import constants

from . import _get_test_name
from . import client, setup_teardown
assert client
assert setup_teardown


@pytest.fixture
def storage_pool(request):
    return StoragePool.all()[-1]


@pytest.fixture
def system(request):
    return System.all()[-1]


def test_get_system():

    assert len(System.all()) == 1


def test_create_volume(storage_pool):

    volume = Volume.create(4, storage_pool["id"], name=_get_test_name(1))

    assert volume.name == _get_test_name(1)
    assert volume.size == 8 * constants.GIGABYTE

    volume.delete()
    with pytest.raises(exceptions.ScaleIOError):
        volume.update()

    # TODO: 'NotFound' error should be 404 instead of 500
    # assert e.value.status_code == 404
    # ScaleIOError: code=500, message=Could not find the volume


def test_volume_resize(storage_pool):

    volume = Volume.create(4, storage_pool["id"], name=_get_test_name(1))

    assert volume.size == 8 * constants.GIGABYTE

    with pytest.raises(exceptions.ScaleIOError) as e:
        volume.resize(10)
    assert e.value.status_code == 400

    with pytest.raises(exceptions.ScaleIOError) as e:
        volume.resize(6)
    assert e.value.status_code == 400

    volume.update()
    assert volume.size == 8 * constants.GIGABYTE

    volume.resize(16)
    volume.update()
    assert volume.size == 16 * constants.GIGABYTE


def test_volume_export(storage_pool, system):

    if system.is_restricted:
        if not Sdc.all_approved():
            pytest.skip("No one approved SDC in restricted mode.")

    volume = Volume.create(8, storage_pool["id"], name=_get_test_name(1))
    assert not volume.exports

    if system.is_restricted:
        sdc = Sdc.all_approved()[-1]
    else:
        sdc = Sdc.all()[-1]

    volume.export(sdc_id=sdc["id"])
    volume.update()

    assert volume.exports
    assert len(volume.exports) == 1
    assert volume.exports[0]["sdcId"] == sdc["id"]
    assert volume.exports[0]["sdcIp"] == sdc.ip

    with pytest.raises(exceptions.ScaleIOError):
        volume.export(sdc_id=sdc["id"])
        volume.export(sdc_guid=sdc["guid"])


def test_create_volume_snapshot(storage_pool, system):

    volume = Volume.create(8, storage_pool["id"], name=_get_test_name(1))
    assert volume.size == 8 * constants.GIGABYTE

    snapshot = volume.snapshot(name=_get_test_name("snapshot_1"))
    assert isinstance(snapshot, Volume)

    assert snapshot.name == _get_test_name("snapshot_1")
    assert snapshot.type == constants.VOLUME_TYPE_SNAPSHOT
    assert snapshot["ancestorVolumeId"] == volume["id"]

    snapshot.delete()
    with pytest.raises(exceptions.ScaleIOError):
        snapshot.update()
