# Copyright (c) 2016, Martin P. Hellwig, All Rights Reserved.
"""
Test the commands
"""
# pylint:disable=R0904,C0111,W0212, import-error, too-few-public-methods
# pylint:disable=attribute-defined-outside-init, wrong-import-position
from django.test import TestCase
import os
    

class TestCommonIpRanges(TestCase):
    def test_010_get_ip(self):
        from ..tools import ipranges
        from .common import FTPMock
        ipranges.ftplib = FTPMock()
        for _ in ipranges.get():
            pass
        # Running twice, the second one is to test the cache functionality.
        for _ in ipranges.get():
            pass

        for filename in os.listdir(path=ipranges.TWD):
            if 'x_remove_x' in filename:
                path = os.path.join(ipranges.TWD, filename)
                os.remove(path)

    def test_020_parse_row(self):
        tmp = 'arin|US|ipv6|2001:400::|32|19990803|allocated|04f048163e37eef48'\
              'd891498545eefc0'
        from ..tools import ipranges
        self.assertEqual(5, len(ipranges._parse_row(tmp)))

        no_tld = tmp.replace('US', '')
        self.assertEqual(None, ipranges._parse_row(no_tld))

        no_ver = tmp.replace('ipv6', 'asn')
        self.assertEqual(None, ipranges._parse_row(no_ver))

    def test_030_compact_ranges(self):
        from ..tools import ipranges
        compact = ipranges.CompactRanges()
        compact.add(*['A', 'B', 'C', 2, 5])
        compact.add(*['A', 'B', 'C', 6, 9])
        self.assertEqual([['A', 'B', 'C', 2, 9]],
                         compact.ranges)

    def test_040_local_file(self):
        from ..tools import ipranges
        url = 'http://example.com/somewhere/over/the/rainbow'
        self.assertEqual(None, ipranges._local_file_from_url(url))

    def test_050_parse_latest(self):
        from ..tools import ipranges
        url = 'http://example.com/somewhere/over/the/rainbow'
        self.assertEqual(None, ipranges.parse_latest(url))

    def test_050_parse_latest_mock(self):
        import tempfile
        _,name = tempfile.mkstemp()
        os.close(_)

        with open(name, 'w') as file_write:
            file_write.write('\n'*13)

        def mock(_):
            "mock local from url"
            return name

        from ..tools import ipranges
        ipranges._local_file_from_url = mock
        returns = ipranges.parse_latest('')
        os.remove(name)

        self.assertEqual([], returns)


if __name__ == '__main__': # pragma: no cover
    import django
    django.setup()
    django.core.management.call_command('test')
