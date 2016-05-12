from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from pagetimer.models import PageVisit


class EndpointTest(TestCase):
    def test_not_logged_in(self):
        r = self.client.post(
            reverse('pagetimer-endpoint'),
            dict(path='/something/random'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(PageVisit.objects.count(), 1)
        v = PageVisit.objects.all()[0]
        self.assertEqual(v.username, 'anonymous')
        self.assertEqual(v.path, '/something/random')

    def test_logged_in(self):
        u = User.objects.create(username='testuser')
        u.set_password('password')
        u.save()
        self.client.login(username='testuser', password='password')
        r = self.client.post(
            reverse('pagetimer-endpoint'),
            dict(path='/something/random'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(PageVisit.objects.count(), 1)
        v = PageVisit.objects.all()[0]
        self.assertEqual(v.username, 'testuser')
        self.assertEqual(v.path, '/something/random')


class DashboardTest(TestCase):
    def test_loads(self):
        u = User.objects.create(username='testuser', is_superuser=True)
        u.set_password('password')
        u.save()
        self.client.login(username='testuser', password='password')
        r = self.client.get(reverse('pagetimer-dashboard'))
        self.assertEqual(r.status_code, 200)


class FilterTest(TestCase):
    def test_loads(self):
        u = User.objects.create(username='testuser', is_superuser=True)
        u.set_password('password')
        u.save()
        self.client.login(username='testuser', password='password')
        r = self.client.get(reverse('pagetimer-filter'))
        self.assertEqual(r.status_code, 200)
        r = self.client.get(reverse('pagetimer-filter') + "?page=30")
        self.assertEqual(r.status_code, 200)
        r = self.client.get(reverse('pagetimer-filter') + "?page=foo")


class CSVTest(TestCase):
    def test_loads(self):
        u = User.objects.create(username='testuser', is_superuser=True)
        u.set_password('password')
        u.save()
        PageVisit.objects.log_visit('user', 'sessionkey', '127.0.0.1', '/')
        self.client.login(username='testuser', password='password')
        r = self.client.get(reverse('pagetimer-csv'))
        self.assertEqual(r.status_code, 200)


class PurgeTest(TestCase):
    def test_form(self):
        u = User.objects.create(username='testuser', is_superuser=True)
        u.set_password('password')
        u.save()
        self.client.login(username='testuser', password='password')
        r = self.client.get(reverse('pagetimer-purge'))
        self.assertEqual(r.status_code, 200)
        self.assertIn('form', r.context)

    def test_post(self):
        u = User.objects.create(username='testuser', is_superuser=True)
        u.set_password('password')
        u.save()
        self.client.login(username='testuser', password='password')
        r = self.client.post(
            reverse('pagetimer-purge'),
            dict(timestamp='2000-01-01 01:01:01')
        )
        self.assertEqual(r.status_code, 302)
