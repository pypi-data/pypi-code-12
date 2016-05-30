from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import SiteLanguage
from molo.yourwords.models import (YourWordsCompetition,
                                   YourWordsCompetitionEntry,
                                   YourWordsCompetitionIndexPage)


class TestYourWordsViewsTestCase(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.user = self.login()
        self.mk_main()
        # Creates Main language
        self.english = SiteLanguage.objects.create(locale='en')
        # Creates Child language
        self.english = SiteLanguage.objects.create(locale='fr')
        # Create competition index page
        self.competition_index = YourWordsCompetitionIndexPage(
            title='Your words competition', slug='Your-words-competition')
        self.main.add_child(instance=self.competition_index)
        self.competition_index.save_revision().publish()

    def test_yourwords_competition_page(self):
        client = Client()
        client.login(username='superuser', password='pass')

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        comp = YourWordsCompetition.objects.get(slug='test-competition')

        response = client.get('/Your-words-competition/test-competition/')
        self.assertContains(response, 'Test Competition')
        self.assertContains(response, 'This is the description')

    def test_yourwords_validation_for_fields(self):
        client = Client()
        client.login(username='superuser', password='pass')

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        comp = YourWordsCompetition.objects.get(slug='test-competition')

        client.get(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]))

        response = client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        response = client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]),
            {'story_name': 'this is a story'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        response = client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]),
            {'story_name': 'This is a story', 'story_text': 'The text'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        response = client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {
                'story_name': 'This is a story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(YourWordsCompetitionEntry.objects.all().count(), 1)

        response = client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {
                'story_name': 'This is a story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true',
                'hide_real_name': 'true'})
        self.assertEquals(response.status_code, 302)
        self.assertEquals(YourWordsCompetitionEntry.objects.all().count(), 2)

    def test_yourwords_thank_you_page(self):
        client = Client()
        client.login(username='superuser', password='pass')

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        response = client.post(
            reverse('molo.yourwords:competition_entry', args=[comp.slug]), {
                'story_name': 'This is a story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true'})
        self.assertEqual(
            response['Location'],
            '/yourwords/thankyou/test-competition/')

    def test_translated_yourwords_competition_page_exists(self):
        client = Client()
        client.login(username='superuser', password='pass')

        comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=comp)
        comp.save_revision().publish()

        self.client.post(reverse(
            'add_translation', args=[comp.id, 'fr']))
        page = YourWordsCompetition.objects.get(
            slug='french-translation-of-test-competition')
        page.save_revision().publish()

        response = self.client.get(reverse(
            'wagtailadmin_explore', args=[self.competition_index.id]))
        page = YourWordsCompetition.objects.get(
            slug='french-translation-of-test-competition')
        self.assertContains(response,
                            '<a href="/admin/pages/%s/edit/"'
                            % page.id)

    def test_translated_competition_entry_stored_against_the_main_lang(self):
        client = Client()
        client.login(username='superuser', password='pass')

        en_comp = YourWordsCompetition(
            title='Test Competition',
            description='This is the description',
            slug='test-competition')
        self.competition_index.add_child(instance=en_comp)
        en_comp.save_revision().publish()

        self.client.post(reverse(
            'add_translation', args=[en_comp.id, 'fr']))
        fr_comp = YourWordsCompetition.objects.get(
            slug='french-translation-of-test-competition')
        fr_comp.save_revision().publish()

        client.post(
            reverse('molo.yourwords:competition_entry', args=[fr_comp.slug]), {
                'story_name': 'this is a french story',
                'story_text': 'The text',
                'terms_or_conditions_approved': 'true'})

        entry = YourWordsCompetitionEntry.objects.all().first()
        self.assertEqual(entry.story_name, 'this is a french story')
        self.assertEqual(entry.competition.id, en_comp.id)
