class SiteResourceMixin(object):
    """Methods for managing Site resources."""

    def list_sites(self, **options):
        """Return paginated list of sites.

        >>> yola.list_sites()
        {
            'count': 999,
            'previous': None,
            'next': 'https://wl.qa.yola.net/pr/sites/?page=2',
            'results': [{...}, {...}, ...]
        }

        You can pass ``page_size`` and ``page`` as keyword arguments:

        >>> yola.list_sites(page_size=50, page=2)

        You can also pass filters and odering options as keyword arguments.
        See https://wl.qa.yola.net/sites/ for available options.
        """
        return self.get(self._site_path(), params=options).json()

    def get_site(self, site_id):
        """Return details for a particular site.

        >>> site = yola.get_site('site_id')
        >>> site['name']
        'My Site'
        """
        return self.get(self._site_path(site_id)).json()

    def disable_site(self, site_id):
        """Disable a site.

        A disabled site can be edited but can't be published.

        >>> yola.disable_site('site_id')
        """
        self.post(self._site_path(site_id, 'disable'))

    def enable_site(self, site_id):
        """Enable a site.

        >>> yola.enable_site('site_id')
        """
        self.post(self._site_path(site_id, 'enable'))

    def change_site_owner(self, site_id, new_user_id):
        """Change site owner.

        >>> yola.change_site_owner('site_id', 'new_user_id')
        """
        data = {'id': new_user_id}
        self.post(self._site_path(site_id, 'change_owner'), data=data)

    def change_site_domain(self, site_id, new_domain):
        """Change site's domain.

        >>> yola.change_site_domain('site_id', 'newdomain.com')
        """
        data = {'partner_domain': new_domain}
        self.put(self._site_path(site_id, 'partner_domain'), data=data)

    def delete_site(self, site_id):
        """Delete a site.

        >>> yola.get_site('site_id')['deleted_at']
        None
        >>> yola.delete_site('site_id')
        >>> yola.get_site('site_id')['deleted_at']
        '2015-08-27T10:00:07'
        """
        self.delete(self._site_path(site_id))

    def undelete_site(self, site_id):
        """Un-delete a site.

        >>> yola.get_site('site_id')['deleted_at']
        '2015-08-27T10:00:07'
        >>> yola.undelete_site('site_id')
        >>> yola.get_site('site_id')['deleted_at']
        None
        """
        self.post(self._site_path(site_id, 'undelete'))

    def _site_path(self, *parts):
        path = '/'.join(['sites'] + list(parts))
        return '/%s/' % path

    def _create_site(self, **attributes):
        return self.post(self._site_path(), data=attributes).json()
