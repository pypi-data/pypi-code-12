class UserResourceMixin(object):
    """Methods for managing User resources."""

    def create_user(self, **attributes):
        """Create a user.

        >>> user = yola.create_user(
            name='John',
            surname='Smith',
            email='johnsmith@example.com',
            partner_id='WL_PARTNER_ID',
            preferences={'preference_name': 'preference_value'})
        >>> user['name']
        'John'
        """
        response = self.post(self._user_path(), data=attributes).json()
        response['signup_date'] = response.pop('signupDate')
        return response

    def update_user(self, user_id, **attributes):
        """Update a user.

        >>> yola.update_user('user_id', name='New name')
        """
        return self.patch(self._user_path(user_id), data=attributes).json()

    def get_user(self, user_id):
        """Get details for a particular user.

        >>> user = yola.get_user('user_id')
        >>> user['name']
        'John'
        """
        return self.get(self._user_path(user_id)).json()

    def list_users(self, **filters):
        """Return paginated list of users.

        >>> yola.list_users()
        {
            'count': 999,
            'previous': None,
            'next': 'https://wl.qa.yola.net/pr/users/?page=2',
            'results': [
                {'name': 'John', 'surname': 'Smith', ...}
            ]
        }

        If there are no users, ``results`` will be an empty list. No exception
        will be raised.

        You may pass pagination options and attribute filters as keyword
        arguments.  See https://wl.qa.yola.net/users/ for available parameters.

        For example:

        >>> yola.list_users(page=2, page_size=50, partner_id='WL_YOLA')
        """
        return self.get(self._user_path(), params=filters).json()

    def delete_user(self, user_id):
        """Delete a user.

        >>> yola.delete_user('user_id')
        """
        self.delete(self._user_path(user_id))

    def get_sso_create_site_url(self, user_id, domain):
        """Get SSO create site url for a particular user and domain.

        >>> yola.get_sso_create_site_url('user_id', 'example.com')
        """
        return self.get(
            self._user_path(user_id, 'sso_url_create_site'),
            params={'domain': domain}).json()['url']

    def get_sso_open_site_url(self, user_id):
        """Get SSO open site url for a particular user.

        >>> yola.get_sso_open_site_url('user_id')
        """
        return self.get(
            self._user_path(user_id, 'sso_url_open_site')).json()['url']

    def _user_path(self, *parts):
        path = '/'.join(['users'] + list(parts))
        return '/%s/' % path
