import hmac
from email.utils import formatdate
from operator import itemgetter
import webtest
import time

from cubicweb.web.controller import Controller
from cubes.signedrequest import includeme
from cubes.signedrequest.tools import HEADERS_TO_SIGN

class TestController(Controller):
    __regid__ = 'testauth'

    def publish(self, rset):
        if self._cw.user.login == self._cw.form.get('expected', 'admin'):
            return 'VALID'
        else:
            return 'INVALID'

class SignedRequestBaseTC(object):
    test_db_id = 'signedresquest'
    def includeme(self, config):
        includeme(config)

    def setup_database(self):
        with self.admin_access.repo_cnx() as cnx:
            with cnx.security_enabled(False, False):
                cnx.execute('INSERT AuthToken T: T token "my precious", '
                            '                    T token_for_user U, '
                            '                    T id "admin", '
                            '                    T enabled True'
                            ' WHERE U login "admin"')
                cnx.commit()

    def _assert_auth(self, req, result):
        raise NotImplementedError()
        
    def _assert_auth_failed(self, req, result):
        raise NotImplementedError()
            
    def _build_string_to_sign(self, request):
        raise NotImplementedError()

    def _build_signature(self, id, string_to_sign):
        with self.admin_access.client_cnx() as cnx:
            rset = cnx.execute('Any K WHERE T id %(id)s, T token K',
                               {'id': id})
            assert rset
            return hmac.new(str(rset[0][0]), string_to_sign).hexdigest()

    def _test_header_format(self, method, login, http_method='GET', signature=None,
                            headers=None, content=None, url='/testauth', **params):
        raise NotImplementedError()
    
    def get_valid_authdata(self, headers=None):
        if headers is None:
            headers = {}
        headers.setdefault('Content-MD5', 'd41d8cd98f00b204e9800998ecf8427e')
        headers.setdefault('Content-Type', 'application/xhtml+xml')
        headers.setdefault('Date', formatdate(usegmt=True))
        return headers

    def test_login(self):
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               )
        self._assert_auth(req, result)

    def test_bad_date(self):
        for date in (formatdate(time.time() + 1000, usegmt=True),
                     formatdate(time.time() - 1000, usegmt=True),
                     'toto'):
            headers = {'Date': date}

            result, req = self._test_header_format(method='Cubicweb',
                                                   login='admin',
                                                   headers=headers)
            self._assert_auth_failed(req, result)

    def test_bad_http_auth_method(self):
        signature = self._build_signature('admin', '')
        result, req = self._test_header_format(method='AWS', login='admin', signature=signature)
        self._assert_auth_failed(req, result)

    def test_bad_signature(self):
        result, req = self._test_header_format(method='Cubicweb', login='admin', signature='YYY')
        self._assert_auth_failed(req, result)

    def test_deactivated_token(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.execute('SET T enabled False WHERE T token_for_user U, U login %(l)s',
                        {'l':'admin'})
            cnx.commit()
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               )
        self._assert_auth_failed(req, result)

    def test_bad_signature_url(self):
        def bad_build_string_to_sign(req):
            get_headers = itemgetter(*HEADERS_TO_SIGN)
            return ''.join(get_headers(req.headers))
        orig = self._build_string_to_sign
        self._build_string_to_sign = bad_build_string_to_sign
        try:
            result, req = self._test_header_format(method='Cubicweb', login='admin', signature='YYY')
            self._assert_auth_failed(req, result)
        finally:
            self._build_string_to_sign = orig

    def test_post_http_request_signature(self):
        headers = {'Content-MD5': '43115f65c182069f76b56df967e5c3fd',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Date': formatdate(usegmt=True)}
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               http_method='POST',
                                               headers=headers)
        self._assert_auth(req, result)

    def test_post_http_request_signature_with_multipart(self):
        date = formatdate(usegmt=True)
        headers = {'Content-MD5': 'f47787068b27ee123d28392f2d21cf70',
                   'Content-Type': 'multipart/form-data; boundary=a71da6eca73a45459439dd288f8185a4',
                   'Date': date}
        string_to_sign = 'POSThttp://testing.fr/cubicweb/testauth?key1=value1f47787068b27ee123d28392f2d21cf70multipart/form-data; boundary=a71da6eca73a45459439dd288f8185a4%s' % date
        body = '--a71da6eca73a45459439dd288f8185a4\r\nContent-Disposition: form-data; name="datak1"\r\n\r\nsome content\r\n--a71da6eca73a45459439dd288f8185a4\r\nContent-Disposition: form-data; name="filename"; filename="filename"\r\nContent-Type: application/octet-stream\r\n\r\nabc\r\n--a71da6eca73a45459439dd288f8185a4--\r\n'
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               content=body,
                                               http_method='POST',
                                               headers=headers,
                                               url='/testauth?key1=value1'
                                               )
        self._assert_auth(req, result)

    def test_post_http_request_signature_with_data(self):
        date = formatdate(usegmt=True)
        headers = {'Content-MD5': '9893532233caff98cd083a116b013c0b',
                   'Date': date}
        string_to_sign = 'POSThttp://testing.fr/cubicweb/testauth?key1=value19893532233caff98cd083a116b013c0b%s' % date
        body = 'some content'
        result, req = self._test_header_format(method='Cubicweb',
                                               login='admin',
                                               content=body,
                                               http_method='POST',
                                               headers=headers,
                                               url='/testauth?key1=value1'
                                               )
        self._assert_auth(req, result)
