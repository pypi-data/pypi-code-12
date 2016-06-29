import pytest
from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy

from molo.usermetadata.models import PersonaIndexPage, PersonaPage


@pytest.mark.django_db
class TestPages(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.english = SiteLanguage.objects.create(locale='en')
        self.mk_main()

        self.index = PersonaIndexPage(title='Personae', slug="personae")
        self.main.add_child(instance=self.index)
        self.index.save_revision().publish()

        self.page = PersonaPage(title="child", slug="child")
        self.index.add_child(instance=self.page)
        self.page.save_revision().publish()

        self.client = Client()
        # Login
        self.user = self.login()

        site = Site.objects.get(is_default_site=True)
        setting = SettingsProxy(site)
        self.persona_settings = setting['usermetadata']['PersonaeSettings']
        self.persona_settings.persona_required = True
        self.persona_settings.save()

        self.site_settings = setting['core']['SiteSettings']
        self.site_settings.ga_tag_manager = 'GTM-xxxx'
        self.site_settings.save()

    def test_persona_selected_tag(self):

        response = self.client.get('/')
        self.assertRedirects(
            response, reverse('molo.usermetadata:persona') + '?next=/')

        response = self.client.get('%s?next=%s' % ((
            reverse(
                'molo.usermetadata:set_persona',
                kwargs={'persona_id': self.page.pk})),
            '/'))

        self.assertTrue(self.client.session['MOLO_PERSONA_SELECTED'])

        response = self.client.get('/')
        self.assertContains(response, 'persona=child')
