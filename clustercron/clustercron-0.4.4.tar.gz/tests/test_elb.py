"""
Tests for `clustercron` module.
"""

from __future__ import print_function
from __future__ import unicode_literals
import pytest
import requests
import responses
from clustercron import elb


class Inst_health_state(object):
    def __init__(self, instance_id, state):
        self.instance_id = instance_id
        self.state = state


def test_Elb_init():
    '''
    Test Elb attributes set by __init__.
    '''
    lb = elb.Elb('mylbname')
    assert lb.__dict__ == {
        'lb_name': 'mylbname',
        'timeout': 3,
    }


@responses.activate
def test_Elb_get_instance_id_returns_instance_id():
    '''
    Test Elb _get_instance_id return instance id.
    '''
    URL_INSTANCE_ID = 'http://169.254.169.254/1.0/meta-data/instance-id'
    INSTANCE_ID = 'i-58e224a1'

    responses.add(
        responses.GET,
        URL_INSTANCE_ID,
        status=200,
        content_type='text/plain',
        body=INSTANCE_ID,
    )

    lb = elb.Elb('mylbname')
    instance_id = lb._get_instance_id()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == URL_INSTANCE_ID
    assert responses.calls[0].response.text == INSTANCE_ID
    assert instance_id == INSTANCE_ID


@responses.activate
def test_Elb_get_instance_id_returns_None_on_HTTPError():
    '''
    test Elb get instance id returns None on HTTPError.
    '''
    URL_INSTANCE_ID = 'http://169.254.169.254/1.0/meta-data/instance-id'

    responses.add(
        responses.GET,
        URL_INSTANCE_ID,
        body=requests.exceptions.HTTPError()
    )

    lb = elb.Elb('mylbname')
    instance_id = lb._get_instance_id()

    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == URL_INSTANCE_ID
    assert instance_id is None


def test_get_inst_health_states_returns_empty_list_at_exception(monkeypatch):
    '''
    Test Elb `clustercron._get_inst_health_states` returns empty list when some
    exception is raised.
    '''
    class ELBConnectionMock(object):
        def get_all_load_balancers(self, load_balancer_names):
            raise Exception('Some exception')

    monkeypatch.setattr('boto.ec2.elb.ELBConnection', ELBConnectionMock)

    lb = elb.Elb('mylbname')
    assert lb._get_inst_health_states() == []


def test_get_inst_health_states_returns_instance_health_states(monkeypatch):
    '''
    Test Elb `clustercron._get_inst_health_states` returns
    intance_health_states
    '''
    instance_health_states = [
        Inst_health_state('i-cba0ce84', 'InService'),
        Inst_health_state('i-1d564f5c', 'InService'),
    ]

    class LoadBalancerMock(object):
        def get_instance_health(self):
            return instance_health_states

    class ELBConnectionMock(object):
        def get_all_load_balancers(self, load_balancer_names):
            return [LoadBalancerMock()]

    monkeypatch.setattr('boto.ec2.elb.ELBConnection', ELBConnectionMock)

    lb = elb.Elb('mylbname')
    assert lb._get_inst_health_states() == instance_health_states


@pytest.mark.parametrize('instance_id,inst_health_states,is_master', [
    (
        u'i-1d564f5c',
        [
            {'instance_id': u'i-1d564f5c', 'state': u'InService'},
            {'instance_id': u'i-cba0ce84', 'state': u'InService'},
        ],
        True,
    ),
    (
        u'i-1d564f5c',
        [
            {'instance_id': u'i-cba0ce84', 'state': u'InService'},
            {'instance_id': u'i-1d564f5c', 'state': u'InService'},
        ],
        True,
    ),
    (
        u'i-1d564f5c',
        [
            {'instance_id': u'i-cba0ce84', 'state': u'Anything'},
            {'instance_id': u'i-1d564f5c', 'state': u'InService'},
        ],
        True,
    ),
    (
        u'i-cba0ce84',
        [
            {'instance_id': u'i-1d564f5c', 'state': u'InService'},
            {'instance_id': u'i-cba0ce84', 'state': u'InService'},
        ],
        False,
    ),
    (
        u'i-cba0ce84',
        [
            {'instance_id': u'i-cba0ce84', 'state': u'InService'},
            {'instance_id': u'i-1d564f5c', 'state': u'InService'},
        ],
        False,
    ),
    (
        u'i-cba0ce84',
        [
            {'instance_id': u'i-cba0ce84', 'state': u'InService'},
            {'instance_id': u'i-1d564f5c', 'state': u'anything'},
        ],
        True,
    ),
    (
        None,
        [
            {'instance_id': u'i-1d564f5c', 'state': u'InService'},
            {'instance_id': u'i-cba0ce84', 'state': u'InService'},
        ],
        False,
    ),
    (
        None,
        [
            {'instance_id': u'i-1d564f5c', 'state': u'InService'},
            {'instance_id': u'i-cba0ce84', 'state': u'InService'},
        ],
        False,
    ),
])
def test_elb_is_master(instance_id, inst_health_states, is_master):
    lb = elb.Elb('mylbname')
    assert lb._is_master(
        instance_id,
        [Inst_health_state(**x) for x in inst_health_states]) == is_master


def test_Elb_master_returns_True(monkeypatch):
    '''
    Test if `Elb.master` returns True
    '''
    instance_health_states = [
        Inst_health_state('i-cba0ce84', 'InService'),
        Inst_health_state('i-1d564f5c', 'InService'),
    ]
    monkeypatch.setattr(elb.Elb, '_get_instance_id', lambda self: 'i-1d564f5c')
    monkeypatch.setattr(
        elb.Elb,
        '_get_inst_health_states',
        lambda self: instance_health_states,
    )
    lb = elb.Elb('mylbname')
    assert lb.master() is True


def test_Elb_master_returns_False(monkeypatch):
    '''
    Test if `Elb.master` returns False
    '''
    instance_health_states = [
        Inst_health_state('i-cba0ce84', 'InService'),
        Inst_health_state('i-1d564f5c', 'InService'),
    ]
    monkeypatch.setattr(elb.Elb, '_get_instance_id', lambda self: 'i-cba0ce84')
    monkeypatch.setattr(
        elb.Elb,
        '_get_inst_health_states',
        lambda self: instance_health_states,
    )
    lb = elb.Elb('mylbname')
    assert lb.master() is False


def test_Elb_master_returns_False_when_instance_id_is_None(monkeypatch):
    '''
    Test if `Elb.master` returns False when `Elb.instance_id` is None.
    '''
    instance_health_states = [
        Inst_health_state('i-cba0ce84', 'InService'),
        Inst_health_state('i-1d564f5c', 'InService'),
    ]
    monkeypatch.setattr(elb.Elb, '_get_instance_id', lambda self: None)
    monkeypatch.setattr(
        elb.Elb,
        '_get_inst_health_states',
        lambda self: instance_health_states,
    )
    lb = elb.Elb('mylbname')
    assert lb.master() is False
