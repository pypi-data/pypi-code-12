from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import View

from doi_site.settings import DATACITE_TEST_URL, DATACITE_URL

class Mint(View):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(Mint, self).dispatch(*args, **kwargs)

    # pylint: disable=no-self-use
    def get(self, request):
        context = {'is_testing' : _is_test_url()}
        return render(request, 'datasets/mint.html', context)


def _is_test_url():
    if DATACITE_URL == DATACITE_TEST_URL:
        return True
    return False
