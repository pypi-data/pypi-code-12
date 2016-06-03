from Products.Five import BrowserView
from affinitic.caching.memcached import toggle_memcached_usage
from affinitic.caching.memcached import get_memcached_usage
from affinitic.caching.memcached import get_memcached_prefix
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ToggleMemcached(BrowserView):

    template = ViewPageTemplateFile('memcached_usage.pt')

    def __call__(self):
        if self.request.form.get('toggle', False):
            toggle_memcached_usage()
        self.is_memcached_used = get_memcached_usage()
        self.memcached_prefix = get_memcached_prefix()
        return self.template()
