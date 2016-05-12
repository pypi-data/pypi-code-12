from django.test import TestCase
from pagetimer.templatetags.pagetimertags import pagetimer


class TestTemplateTag(TestCase):
    def test_pagetimer(self):
        fake_context = dict()

        r = pagetimer(fake_context)
        self.assertEqual(r['pagetimer_interval'], 60)
        self.assertEqual(r['pagetimer_endpoint'], '/endpoint/')

    def test_pagetimer_with_different_interval(self):
        fake_context = dict()

        with self.settings(PAGETIMER_INTERVAL=10):
            r = pagetimer(fake_context)
            self.assertEqual(r['pagetimer_interval'], 10)
