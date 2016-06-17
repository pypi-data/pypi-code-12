import pytest

from django.test.client import Client
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from vr.server import models
from vr.common.utils import randchars
from vr.server.tests import get_user
from vr.server.utils import yamlize


pytestmark = pytest.mark.usefixtures('postgresql')


class TestSaveSwarms:
    def setup_method(self, method):

        self.app = models.App(
            name=randchars(),
            repo_url=randchars(),
            repo_type=randchars(),
            )
        self.app.save()

        self.app2 = models.App(
            name=randchars(),
            repo_url=randchars(),
            repo_type=randchars(),
            )
        self.app2.save()

        self.build = models.Build(
            app=self.app,
            tag=randchars(),
            file=randchars(),
            status='success',
            hash=randchars(),
            )
        self.build.save()

        self.build2 = models.Build(
            app=self.app2,
            tag=randchars(),
            file=randchars(),
            status='success',
            hash=randchars(),
            )
        self.build2.save()

        self.release = models.Release(
            build=self.build,
            config_yaml='',
            env_yaml='',
            hash=randchars(),
            )
        self.release.save()

        self.release2 = models.Release(
            build=self.build2,
            config_yaml='',
            env_yaml='',
            hash=randchars(),
            )
        self.release2.save()

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

        self.swarm2 = models.Swarm(
            app=self.app2,
            release=self.release2,
            config_name=randchars(),
            proc_name='web',
            squad=self.squad,
        )
        self.swarm2.save()

        dashboard_name = randchars()
        self.dashboard = models.Dashboard(
            name=dashboard_name,
            slug=slugify(dashboard_name),
        )
        self.dashboard.save()
        self.dashboard.apps.add(self.app2)

        # Get a logged in client ready
        self.user = get_user()
        models.UserProfile.objects.create(user=self.user)
        self.user.userprofile.default_dashboard = self.dashboard
        self.user.userprofile.save()
        self.client = Client()
        self.client.post(reverse('login'), {'username': self.user.username, 'password':'password123'})

    def test_simple_update(self, redis):

        url = reverse('edit_swarm', kwargs={'swarm_id':self.swarm.id})
        payload = {
            'app_id': self.swarm.app.id,
            'os_image_id': getattr(self.swarm.release.build.os_image, 'id', ''),
            'squad_id': self.swarm.squad.id,
            'tag': randchars(),
            'config_name': self.swarm.config_name,
            'config_yaml': yamlize(self.swarm.config_yaml),
            'env_yaml': yamlize(self.swarm.env_yaml),
            'volumes': yamlize(self.swarm.volumes),
            'run_as': self.swarm.run_as or 'nobody',
            'mem_limit': self.swarm.mem_limit,
            'memsw_limit': self.swarm.memsw_limit,
            'proc_name': self.swarm.proc_name,
            'size': self.swarm.size,
            'pool': self.swarm.pool or '',
            'balancer': '',
            'config_ingredients': [
                ing.pk for ing in self.swarm.config_ingredients.all()]
        }
        previous_release_id = self.swarm.release_id
        resp = self.client.post(url, data=payload)
        saved = models.Swarm.objects.get(id=self.swarm.id)
        new_release_id = saved.release_id
        assert previous_release_id != new_release_id

    def test_invalid_tags(self):
        url = reverse('edit_swarm', kwargs={'swarm_id':self.swarm.id})
        invalid_tags = [
            'gittag/v1',
            'my:tag',
            '^tag',
            '~other:tag',
            'tag?'
            'other*tag'
            '\\tag',
            'a tag'
        ]
        payload = {
            'app_id': self.swarm.app.id,
            'os_image_id': getattr(self.swarm.release.build.os_image, 'id', ''),
            'squad_id': self.swarm.squad.id,
            'config_name': self.swarm.config_name,
            'config_yaml': yamlize(self.swarm.config_yaml),
            'env_yaml': yamlize(self.swarm.env_yaml),
            'volumes': yamlize(self.swarm.volumes),
            'run_as': self.swarm.run_as or 'nobody',
            'mem_limit': self.swarm.mem_limit,
            'memsw_limit': self.swarm.memsw_limit,
            'proc_name': self.swarm.proc_name,
            'size': self.swarm.size,
            'pool': self.swarm.pool or '',
            'balancer': '',
            'config_ingredients': [
                ing.pk for ing in self.swarm.config_ingredients.all()]
        }
        for tag in invalid_tags:
            payload['tag'] = tag
            resp = self.client.post(url, data=payload)
            assert 'Invalid tag name' in resp.content

    def test_normal_app_update_redirection(self, redis):
        """
        Test that after swarming an app not in the user's default dashboard,
        he/she gets redirected to the 'Home' section.

        See self.setUp() for more info.
        """
        url = reverse('edit_swarm', kwargs={'swarm_id': self.swarm.id})
        payload = {
            'app_id': self.swarm.app.id,
            'os_image_id': getattr(self.swarm.release.build.os_image, 'id', ''),
            'squad_id': self.swarm.squad.id,
            'tag': randchars(),
            'config_name': self.swarm.config_name,
            'config_yaml': yamlize(self.swarm.config_yaml),
            'env_yaml': yamlize(self.swarm.env_yaml),
            'volumes': yamlize(self.swarm.volumes),
            'run_as': self.swarm.run_as or 'nobody',
            'mem_limit': self.swarm.mem_limit,
            'memsw_limit': self.swarm.memsw_limit,
            'proc_name': self.swarm.proc_name,
            'size': self.swarm.size,
            'pool': self.swarm.pool or '',
            'balancer': '',
            'config_ingredients': [
                ing.pk for ing in self.swarm.config_ingredients.all()]
        }
        resp = self.client.post(url, data=payload)
        assert resp._headers['location'][1] == 'http://testserver/'

    def test_dashboard_app_update_redirection(self, redis):
        """
        Test that after swarming an app that belongs to the user's default
        dashboard, he/she gets redirected to /dashboard/.

        See self.setUp() for more info.
        """
        url = reverse('edit_swarm', kwargs={'swarm_id': self.swarm2.id})
        payload = {
            'app_id': self.swarm2.app.id,
            'os_image_id': getattr(self.swarm2.release.build.os_image, 'id', ''),
            'squad_id': self.swarm2.squad.id,
            'tag': randchars(),
            'config_name': self.swarm2.config_name,
            'config_yaml': yamlize(self.swarm2.config_yaml),
            'env_yaml': yamlize(self.swarm2.env_yaml),
            'volumes': yamlize(self.swarm2.volumes),
            'run_as': self.swarm2.run_as or 'nobody',
            'mem_limit': self.swarm2.mem_limit,
            'memsw_limit': self.swarm2.memsw_limit,
            'proc_name': self.swarm2.proc_name,
            'size': self.swarm2.size,
            'pool': self.swarm2.pool or '',
            'balancer': '',
            'config_ingredients': [
                ing.pk for ing in self.swarm2.config_ingredients.all()]
        }
        resp = self.client.post(url, data=payload)
        assert resp._headers['location'][1] == 'http://testserver/dashboard/'

    def test_config_yaml_marshaling(self):

        url = reverse('edit_swarm', kwargs={'swarm_id':self.swarm.id})
        payload = {
            'app_id': self.swarm.app.id,
            'os_image_id': getattr(self.swarm.release.build.os_image, 'id', ''),
            'squad_id': self.swarm.squad.id,
            'tag': randchars(),
            'config_name': self.swarm.config_name,
            'config_yaml': '1: integer key not allowed',
            'env_yaml': yamlize(self.swarm.env_yaml),
            'volumes': yamlize(self.swarm.volumes),
            'run_as': self.swarm.run_as or 'nobody',
            'mem_limit': self.swarm.mem_limit,
            'memsw_limit': self.swarm.memsw_limit,
            'proc_name': self.swarm.proc_name,
            'size': self.swarm.size,
            'pool': self.swarm.pool or '',
            'balancer': '',
            'config_ingredients': [
                ing.pk for ing in self.swarm.config_ingredients.all()]
        }
        resp = self.client.post(url, data=payload)
        assert "Cannot be marshalled to XMLRPC" in resp.content

    def test_env_yaml_marshaling(self):

        url = reverse('edit_swarm', kwargs={'swarm_id':self.swarm.id})
        payload = {
            'app_id': self.swarm.app.id,
            'os_image_id': getattr(self.swarm.release.build.os_image, 'id', ''),
            'squad_id': self.swarm.squad.id,
            'tag': randchars(),
            'config_name': self.swarm.config_name,
            'config_yaml': yamlize(self.swarm.config_yaml),
            'env_yaml': 'TOO_BIG_NUMBER: 1234123412341234',
            'volumes': yamlize(self.swarm.volumes),
            'run_as': self.swarm.run_as or 'nobody',
            'mem_limit': self.swarm.mem_limit,
            'memsw_limit': self.swarm.memsw_limit,
            'proc_name': self.swarm.proc_name,
            'size': self.swarm.size,
            'pool': self.swarm.pool or '',
            'balancer': '',
            'config_ingredients': [
                ing.pk for ing in self.swarm.config_ingredients.all()]
        }
        resp = self.client.post(url, data=payload)
        assert "Cannot be marshalled to XMLRPC" in resp.content


class TestSaveIngredients:
    def setup_method(self, method):

        # Get a logged in client ready
        self.user = get_user()
        self.client = Client()
        self.client.post(reverse('login'), {'username': self.user.username, 'password':'password123'})

    def test_save_unmarshalable_ingredient(self):

        url = reverse('ingredient_add')
        payload = {
            'config_yaml': 'TOO_BIG: 1234123412341234',
        }
        resp = self.client.post(url, data=payload)

        assert "Cannot be marshalled to XMLRPC" in resp.content
