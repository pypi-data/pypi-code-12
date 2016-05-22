import pytest
import mock

from django_toolset.decorators import authenticated_redirect

@pytest.mark.urls('utils.tests.test_urls')
class DescribeAuthenticatedRedirect:
    """Test the authenticated_redirect decorator"""
    @classmethod
    def setup_class(cls):
        cls.request = mock.Mock()
        cls.request.path = '/login/'

    def it_works_without_kwargs(self):
        @authenticated_redirect
        def my_function(request):
            return True

        self.request.user.is_authenticated = mock.MagicMock(return_value=True)
        result = my_function(self.request)
        assert result.url == '/dashboard/'

    def it_works_with_kwargs_authenticated(self):
        @authenticated_redirect(path='home')
        def my_function(request):
            return True

        self.request.user.is_authenticated = mock.MagicMock(return_value=True)
        result = my_function(self.request)
        assert result.url == '/'

    def it_works_with_kwargs_unauthenticated(self):
        @authenticated_redirect(path='home')
        def my_function(request):
            return True

        self.request.user.is_authenticated = mock.MagicMock(return_value=False)
        result = my_function(self.request)
        assert result is True

    def it_avoids_redirect_loop(self):
        @authenticated_redirect(path='login')
        def my_function(request):
            return True

        self.request.user.is_authenticated = mock.MagicMock(return_value=True)
        result = my_function(self.request)
        assert result.url == '/dashboard/'
