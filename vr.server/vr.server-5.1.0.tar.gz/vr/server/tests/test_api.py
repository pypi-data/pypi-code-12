import base64
import json

import pytest
from django.test.client import Client
from django.core.urlresolvers import reverse

from vr.common.utils import randchars
from vr.server.tests import get_user
from vr.server import models


def get_api_url(resource_name, view_name, **kwargs):
    kwargs.update({'resource_name': resource_name, 'api_name': 'v1'})
    return reverse(view_name, kwargs=kwargs)


class BasicAuthClient(Client):
    """
    Modified Django test client for conviently doing basic auth.  Pass in
    username and password on init.
    """
    def __init__(self, username, password, *args, **kwargs):
        token = base64.b64encode('{username}:{password}'.format(**locals()))
        self.auth_headers = dict(HTTP_AUTHORIZATION='Basic ' + token)
        super(BasicAuthClient, self).__init__(*args, **kwargs)

    def request(self, *args, **kwargs):
        kwargs.update(self.auth_headers)
        return super(BasicAuthClient, self).request(*args, **kwargs)


def test_no_auth_denied():
    c = Client()
    url = get_api_url('hosts', 'api_dispatch_list')
    response = c.get(url)
    assert response.status_code == 401


def test_basic_auth_accepted(postgresql):
    u = get_user()
    c = BasicAuthClient(u.username, 'password123')
    url = get_api_url('hosts', 'api_dispatch_list')
    response = c.get(url)
    assert response.status_code == 200


def test_basic_auth_bad_password(postgresql):
    u = get_user()
    c = BasicAuthClient(u.username, 'BADPASSWORD')
    url = get_api_url('hosts', 'api_dispatch_list')
    response = c.get(url)
    assert response.status_code == 401


def test_session_auth_accepted(postgresql):
    u = get_user()
    c = Client()
    data = dict(username=u.username, password='password123')
    c.post(reverse('login'), data)
    url = get_api_url('hosts', 'api_dispatch_list')
    response = c.get(url)
    assert response.status_code == 200


def test_config_xmlrpc_marshaling(postgresql):
    u = get_user()
    c = BasicAuthClient(u.username, 'password123')
    url = get_api_url('ingredients', 'api_dispatch_list')
    #data = json.dumps({'config_yaml': {1: 'int key'}})
    #data = json.dumps({'config_yaml': '"bigint": 123412341234}'})
    data = json.dumps({
        'name': randchars(),
        'config_yaml': "{'really_big_int': 1234123412341234}"
    })
    resp = c.post(url, data=data, content_type='application/json')
    assert "int exceeds XML-RPC limits" in resp.content


@pytest.mark.usefixtures('postgresql')
class TestSaveSwarms:

    def setup_method(self, method):
        self.app = models.App(
            name=randchars(),
            repo_url=randchars(),
            repo_type=randchars(),
            )
        self.app.save()

        self.build = models.Build(
            app=self.app,
            tag=randchars(),
            file=randchars(),
            status='success',
            hash=randchars(),
            )
        self.build.save()

        self.release = models.Release(
            build=self.build,
            config_yaml='',
            env_yaml='',
            hash=randchars(),
            )
        self.release.save()

        self.squad=models.Squad(name=randchars())
        self.squad.save()

        # create a swarm object
        self.swarm = models.Swarm(
            app=self.app,
            release=self.release,
            config_name=randchars(),
            proc_name='web',
            squad=self.squad,
        )
        self.swarm.save()

        # Get a logged in client ready
        self.user = get_user()
        self.client = Client()
        data = dict(username=self.user.username, password='password123')
        self.client.post(reverse('login'), data)

    def test_simple_update(self):

        url = get_api_url('swarms', 'api_dispatch_detail', pk=self.swarm.id)
        resp = self.client.get(url)
        doc = json.loads(resp.content)
        assert doc['config_name'] == self.swarm.config_name

        # make a change, PUT it, and assert that it's in the DB.
        doc['config_name'] = 'test_config_name'
        payload = json.dumps(doc)
        resp = self.client.put(url, data=payload,
            content_type='application/json')

        saved = models.Swarm.objects.get(id=self.swarm.id)
        assert saved.config_name == 'test_config_name'

    def test_update_with_ingredient(self):
        ing = models.ConfigIngredient(
            name=randchars(),
            config_yaml='',
            env_yaml='',
            )
        ing.save()
        self.swarm.config_ingredients.add(ing)

        url = get_api_url('swarms', 'api_dispatch_detail', pk=self.swarm.id)
        resp = self.client.get(url)
        doc = json.loads(resp.content)
        assert doc['config_name'] == self.swarm.config_name

        # make a change, PUT it, and assert that it's in the DB.
        doc['config_name'] = 'test_config_name'
        payload = json.dumps(doc)
        resp = self.client.put(url, data=payload,
            content_type='application/json')

        saved = models.Swarm.objects.get(id=self.swarm.id)
        assert saved.config_name == 'test_config_name'

    def test_release(self, redis):
        u = get_user()
        c = BasicAuthClient(u.username, 'password123')
        url = get_api_url('releases', 'api_deploy_release', pk=self.release.id)
        response = c.post(
            url,
            content_type="application/json",
            data=json.dumps({
                'config_name': 'config_name',
                'host': 'host',
                'proc': 'proc',
                'port': 'port',
            }))
        assert response.status_code == 202


class TestAppURL:

    @pytest.fixture
    def simple_app(self, postgresql):
        app = models.App(
            name=randchars(),
            repo_url=randchars(),
            repo_type=randchars(),
        )
        app.save()
        return app

    @pytest.fixture
    def client(self):
        user = get_user()
        client = Client()
        data = dict(username=user.username, password='password123')
        client.post(reverse('login'), data)
        return client

    def test_resolved_url(self, simple_app, client, monkeypatch):
        def clean_url(cmd):
            return "https://clean.example.com/path\n"
        monkeypatch.setattr('subprocess.check_output', clean_url)

        url = get_api_url('apps', 'api_dispatch_detail', name=simple_app.name)
        resp = client.get(url)
        doc = json.loads(resp.content)
        assert doc['resolved_url'] == 'https://clean.example.com/path'

    def test_no_resolved_url(self, simple_app, client, monkeypatch):
        def raise_exc(cmd):
            raise Exception("Failed to run command")
        monkeypatch.setattr('subprocess.check_output', raise_exc)

        url = get_api_url('apps', 'api_dispatch_detail', name=simple_app.name)
        resp = client.get(url)
        doc = json.loads(resp.content)
        assert doc['resolved_url'] == doc['repo_url']
