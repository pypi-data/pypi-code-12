import time
import threading

import pytest

from utvsapitoken import TokenClient
from utvsapitoken.exceptions import TokenInvalid
from utvsapitoken.fakeserver import serve_forever


class TestClient:
    @classmethod
    def setup_class(cls):
        p = pytest.config.getoption('--port')

        t = threading.Thread(target=serve_forever, args=[int(p)])
        t.daemon = True
        t.start()

        time.sleep(1)

        cls.tc = TokenClient(check_token_uri='http://localhost:%s/token' % p,
                             usermap_uri='http://localhost:%s/user' % p)

    def test_fake_token_number(self, port):
        info = self.tc.token_to_info('12345')
        assert info['personal_number'] == 12345
        assert info['scope'] == ['cvut:utvs:general:read',
                                 'cvut:utvs:enrollments:by-role']

    def test_fake_token_god(self, port):
        info = self.tc.token_to_info('GODGODGOD')
        assert 'personal_number' not in info
        assert info['scope'] == ['cvut:utvs:general:read',
                                 'cvut:utvs:enrollments:all']

    def test_fake_token_bad(self, port):
        with pytest.raises(TokenInvalid):
            info = self.tc.token_to_info('bad_token')
