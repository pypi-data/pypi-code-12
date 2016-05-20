# encoding: utf-8

import sys
import unittest

from docido_sdk.toolbox.text import exception_to_unicode, to_unicode


class TestText(unittest.TestCase):
    @classmethod
    def _inner_raise(cls, level):
        if level == 0:
            raise Exception("throwing exception")
        else:
            try:
                cls._inner_raise(level - 1)
            except Exception as e:
                traceback = sys.exc_info()[2]
                raise e, None, traceback

    def test_exception(self):
        try:
            self._inner_raise(3)
        except Exception as e:
            self.assertEqual(
                u"Exception: throwing exception",
                exception_to_unicode(e)
            )
            occurences = filter(
                lambda s: "_inner_raise" in s,
                exception_to_unicode(e, True).split('\n')
            )
            self.assertEqual(len(occurences), 8)

    def test_to_unicode_invalid_charset(self):
        unicode_s = u"❤ ☀ ☆ ☂"
        utf_8_s = unicode_s.encode('utf-8')
        with self.assertRaises(LookupError):
            to_unicode(utf_8_s, 'latin-42')

    def test_to_unicode_utf_8(self):
        self._validate_unicode_conversion(u"❤ ☀ ☆ ☂", 'utf-8')

    def _validate_unicode_conversion(self, unicode_s, charset):
        charset_s = unicode_s.encode(charset)
        self.assertEqual(unicode_s, to_unicode(charset_s, charset))
        self.assertEqual(unicode_s, to_unicode(charset_s))
        self.assertEqual(unicode_s, to_unicode(Exception(charset_s)))

    def test_to_unicode_latin_1_charset(self):
        self._validate_unicode_conversion(u"éà", 'latin-1')

    def test_to_unicode_exception(self):
        unicode_s = u"❤ ☀ ☆ ☂"
        e = Exception(unicode_s)
        self.assertEqual(to_unicode(e), unicode_s)
        unicode_s = u"éà"
        e = Exception(unicode_s.encode('latin-1'))
        self.assertEqual(to_unicode(e), unicode_s)


if __name__ == '__main__':
    unittest.main()
