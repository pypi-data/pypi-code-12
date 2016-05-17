from bs4 import BeautifulSoup
from datetime import datetime

from django.conf.urls import patterns, url, include
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase, Client, override_settings

from molo.commenting.models import MoloComment
from molo.commenting.forms import MoloCommentForm
from molo.core.models import ArticlePage


urlpatterns = patterns(
    '',
    url(r'^commenting/', include('molo.commenting.urls')),
)


@override_settings(ROOT_URLCONF='molo.commenting.tests.test_views')
class ViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')
        self.content_type = ContentType.objects.get_for_model(self.user)
        self.client = Client()
        self.client.login(username='test', password='test')

    def mk_comment(self, comment):
        return MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.user.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            submit_date=datetime.now())

    def test_reporting_without_removal(self):
        comment = self.mk_comment('the comment')
        response = self.client.get(
            reverse('molo-comments-report', args=(comment.pk,)))
        self.assertEqual(response.status_code, 302)
        [flag] = comment.flags.all()
        self.assertEqual(flag.comment, comment)
        self.assertEqual(flag.user, self.user)
        self.assertFalse(MoloComment.objects.get(pk=comment.pk).is_removed)
        self.assertTrue('The comment has been reported.'
                        in response.cookies['messages'].value)

    def test_reporting_with_removal(self):
        comment = self.mk_comment('the comment')
        with self.settings(COMMENTS_FLAG_THRESHHOLD=1):
            response = self.client.get(
                reverse('molo-comments-report', args=(comment.pk,)))
        self.assertEqual(response.status_code, 302)
        [flag] = comment.flags.all()
        self.assertEqual(flag.comment, comment)
        self.assertEqual(flag.user, self.user)
        self.assertTrue(MoloComment.objects.get(pk=comment.pk).is_removed)
        self.assertTrue('The comment has been reported.'
                        in response.cookies['messages'].value)

    def test_molo_post_comment(self):
        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo',
        })
        self.client.post(
            reverse('molo-comments-post'), data)
        [comment] = MoloComment.objects.filter(user=self.user)
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'the supplied name')

    def test_molo_post_comment_anonymous(self):
        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo',
            'submit_anonymously': '1',
        })
        self.client.post(
            reverse('molo-comments-post'), data)
        [comment] = MoloComment.objects.filter(user=self.user)
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'Anonymous')
        self.assertEqual(comment.user_email, self.user.email)

    def test_molo_post_comment_without_email_address(self):
        self.user.email = ''
        self.user.save()

        data = MoloCommentForm(self.user, {}).generate_security_data()
        data.update({
            'name': 'the supplied name',
            'comment': 'Foo',
        })
        self.client.post(
            reverse('molo-comments-post'), data)
        [comment] = MoloComment.objects.filter(user=self.user)
        self.assertEqual(comment.comment, 'Foo')
        self.assertEqual(comment.user_name, 'the supplied name')
        self.assertEqual(comment.user_email, 'blank@email.com')

    def test_report_response(self):
        article = ArticlePage.objects.create(
            title='article 1', depth=1,
            subtitle='article 1 subtitle',
            slug='article-1', path=[1])
        comment = MoloComment.objects.create(
            content_object=article, object_pk=article.id,
            content_type=ContentType.objects.get_for_model(article),
            site=Site.objects.get_current(), user=self.user,
            comment='comment 1', submit_date=datetime.now())
        response = self.client.get(reverse('report_response',
                                   args=(comment.id,)))
        self.assertContains(
            response,
            "This comment has been reported."
        )

    def test_commenting_closed(self):
        article = ArticlePage.objects.create(
            title='article 1', depth=1,
            subtitle='article 1 subtitle',
            slug='article-1', path=[1], commenting_state='C')
        article.save()
        initial = {
            'object_pk': article.id,
            'content_type': "core.articlepage"
        }
        data = MoloCommentForm(article, {},
                               initial=initial).generate_security_data()
        data.update({
            'comment': "This is another comment"
        })
        response = self.client.post(reverse('molo-comments-post'), data)
        self.assertEqual(response.status_code, 302)

    def test_commenting_open(self):
        article = ArticlePage.objects.create(
            title='article 1', depth=1,
            subtitle='article 1 subtitle',
            slug='article-1', path=[1], commenting_state='O')
        article.save()
        initial = {
            'object_pk': article.id,
            'content_type': "core.articlepage"
        }
        data = MoloCommentForm(article, {},
                               initial=initial).generate_security_data()
        data.update({
            'comment': "This is a second comment",
        })
        response = self.client.post(reverse('molo-comments-post'), data)
        self.assertEqual(response.status_code, 302)


@override_settings(ROOT_URLCONF='molo.commenting.tests.test_views')
class ViewMoreCommentsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')
        self.article = ArticlePage.objects.create(
            title='article 1', depth=1,
            subtitle='article 1 subtitle',
            slug='article-1', path=[1])

        self.client = Client()

    def create_comment(self, comment, parent=None):
        return MoloComment.objects.create(
            content_type=ContentType.objects.get_for_model(self.article),
            object_pk=self.article.pk,
            content_object=self.article,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            parent=parent,
            submit_date=datetime.now())

    def test_view_more_comments(self):
        for i in range(50):
            self.create_comment('comment %d' % i)
        response = self.client.get(
            reverse('more-comments', args=[self.article.pk, ],))
        self.assertContains(response, 'Page 1 of 3')
        self.assertContains(response, '&rarr;')
        self.assertNotContains(response, '&larr;')

        response = self.client.get(
            '%s?p=2' % (reverse('more-comments', args=[self.article.pk, ],),))
        self.assertContains(response, 'Page 2 of 3')
        self.assertContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

        response = self.client.get(
            '%s?p=3' % (reverse('more-comments', args=[self.article.pk, ],),))
        self.assertContains(response, 'Page 3 of 3')
        self.assertNotContains(response, '&rarr;')
        self.assertContains(response, '&larr;')

    def test_view_page_not_integer(self):
        '''If the requested page number is not an integer, the first page
        should be returned.'''
        response = self.client.get(
            '%s?p=foo' % reverse('more-comments', args=(self.article.pk,)))
        self.assertContains(response, 'Page 1 of 1')

    def test_view_empty_page(self):
        '''If the requested page number is too large, it should show the
        last page.'''
        for i in range(40):
            self.create_comment('comment %d' % i)
        response = self.client.get(
            '%s?p=3' % reverse('more-comments', args=(self.article.pk,)))
        self.assertContains(response, 'Page 2 of 2')

    def test_view_nested_comments(self):
        comment1 = self.create_comment('test comment1 text')
        comment2 = self.create_comment('test comment2 text')
        comment3 = self.create_comment('test comment3 text')
        reply1 = self.create_comment('test reply1 text', parent=comment2)
        reply2 = self.create_comment('test reply2 text', parent=comment2)
        response = self.client.get(
            reverse('more-comments', args=(self.article.pk,)))

        html = BeautifulSoup(response.content, 'html.parser')
        [c3row, c2row, reply1row, reply2row, c1row] = html.find_all(
            class_='comment')
        self.assertTrue(comment3.comment in c3row.prettify())
        self.assertTrue(comment2.comment in c2row.prettify())
        self.assertTrue(reply1.comment in reply1row.prettify())
        self.assertTrue(reply2.comment in reply2row.prettify())
        self.assertTrue(comment1.comment in c1row.prettify())

    def test_view_replies_report(self):
        '''If a comment is a reply, there should be no report button, as all
        replies are created by admins.'''
        comment = self.create_comment('test comment1 text')
        reply = self.create_comment('test reply text', parent=comment)

        response = self.client.get(
            reverse('more-comments', args=(self.article.pk,)))

        html = BeautifulSoup(response.content, 'html.parser')
        [crow, replyrow] = html.find_all(class_='comment')
        self.assertTrue(comment.comment in crow.prettify())
        self.assertTrue('report' in crow.prettify())
        self.assertTrue(reply.comment in replyrow.prettify())
        self.assertFalse('report' in replyrow.prettify())
