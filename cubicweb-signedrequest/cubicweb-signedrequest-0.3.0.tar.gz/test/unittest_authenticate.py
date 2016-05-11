# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-signedrequest automatic tests for authentication
"""
from StringIO import StringIO

from cubicweb.devtools.testlib import CubicWebTC, real_error_handling

from cubes.signedrequest.tools import HEADERS_TO_SIGN
from cubes.signedrequest.test import TestController, SignedRequestBaseTC


class SignedRequestTC(SignedRequestBaseTC, CubicWebTC):

    def _assert_auth(self, req, result):
        self.assertEqual(200, req.status_out)
        self.assertEqual('VALID', result)

    def _assert_auth_failed(self, req, result):
        if req.status_out == 200:
            self.assertEqual('INVALID', result)
        else:
            self.assertGreater(req.status_out, 400)

    def _build_string_to_sign(self, request):
        return (request.http_method() + request.url() +
                ''.join(request.get_header(header) for header in HEADERS_TO_SIGN))

    def _test_header_format(self, method, login, http_method='GET', signature=None,
                            headers=None, content=None, url='/testauth', **params):
        if headers is None:
            headers = {}
        headers = self.get_valid_authdata(headers)
        with self.temporary_appobjects(TestController):
            url = params.pop('url', TestController.__regid__)
            req = self.requestcls(self.vreg, url=url,
                                  method=http_method, **params)
            req.form['expected'] = 'admin'
            # Fill an arbitrary body content if POST.
            if http_method == 'POST':
                if content is None:
                    content = "rql=Any+X+WHERE+X+is+Player"
                req.content = StringIO(content)
            for name, value in headers.items():
                req.set_request_header(name, value, raw=True)
            if signature is None:
                string_to_sign = self._build_string_to_sign(req)
                signature = self._build_signature('admin', string_to_sign)
            req.set_request_header('Authorization',
                            '%s %s:%s' % (method, login, signature), raw=True)
            with real_error_handling(self.app):
                result = self.app.handle_request(req, 'testauth')
        return result, req



if __name__ == "__main__":
    from logilab.common.testlib import unittest_main
    unittest_main()
