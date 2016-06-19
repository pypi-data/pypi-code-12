# Copyright (c) 2016, Nutonian Inc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the Nutonian Inc nor the
#     names of its contributors may be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL NUTONIAN INC BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


class _Organization:
    def __init__(self, eureqa, name):
        self._eureqa = eureqa
        self.name = name

    def create_user(self, user_email, password, role, first_name, last_name):
        key_url = '/api/v2/%s/auth/signup_key' % self.name
        key_request = {'organization': self.name, 'total_uses': 1, 'roles': ['%s' % role]}
        self._eureqa._session.report_progress('Creating signup_key for role \'%s\'.' % role)
        key = self._eureqa._session.execute(key_url, 'POST', args=key_request)

        body = user_request = {
            'firstname': first_name,
            'lastname': last_name,
            'username': user_email,
            'useremail': user_email,
            'password': password,
            'signup_key': key['signup_key']}
        self._eureqa._session.report_progress('Signing up user: \'%s\'.' % user_email)
        self._eureqa._session.execute('/api/v2/auth/signup', 'POST', args=user_request)

    def _delete_user(self, user_email):
        user_url = '/api/v2/auth/user/%s' % user_email
        self._eureqa._session.report_progress('Deleting user \'%s\'.' % user_email)
        self._eureqa._session.execute(user_url, 'DELETE')

    def _make_user_sys_admin(self, user_email):
        user_url = '/api/v2/auth/user/%s' % user_email
        self._eureqa._session.report_progress('Making user \'%s\' into sysadmin.' % user_email)
        user = self._eureqa._session.execute(user_url, 'GET')
        user["sysadmin"] = True
        self._eureqa._session.execute(user_url, 'POST', args=user)

    def _make_user_user_admin(self, user_email):
        user_url = '/api/v2/auth/user/%s' % user_email
        self._eureqa._session.report_progress('Making user \'%s\' into user_admin.' % user_email)
        user = self._eureqa._session.execute(user_url, 'GET')
        user["user_admin"] = True
        self._eureqa._session.execute(user_url, 'POST', args=user)

    def _set_search_limit(self, limit):
        org = self._eureqa._session.execute('/api/v2/organizations/%s' % self.name, 'GET')
        org['limits']['max_searches'] = limit
        self._eureqa._session.execute('/api/v2/organizations/%s' % self.name, 'POST', args=org)
