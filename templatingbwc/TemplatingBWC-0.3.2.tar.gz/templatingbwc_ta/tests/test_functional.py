from blazeweb.globals import ag
from blazeweb.testing import TestApp

class TestTemplates(object):

    @classmethod
    def setup_class(cls):
        cls.ta = TestApp(ag.wsgi_test_app)

    def test_title_tag(self):
        r = self.ta.get('/')
        assert 'Index | TemplatingBWC Application Administration' in r
        assert 'Change Password' not in r

        r = self.ta.get('/login')
        r = r.follow()
        assert 'Change Password' in r

    def check_200(self, url):
        self.ta.get(url)

    def test_urls(self):
        urls = (
            '/',
            '/typography',
            '/login',
            '/logout',
            '/user-messages',
            '/boxes',
            '/boxes-and-text',
            '/boxes-and-boxes',
            '/modals',
            '/tables',
            '/forms',
            '/jquery-ui',
            '/icons',
        )

        for url in urls:
            yield self.check_200, url
