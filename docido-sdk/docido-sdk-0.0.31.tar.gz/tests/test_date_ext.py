# encoding: utf-8

import datetime
import unittest

from docido_sdk.toolbox.date_ext import timestamp_ms

KIOTO_ISO_8601 = '1997-12-11T17:33:47+00:00'
KIOTO_ISO_8601_TZ = '1997-12-11T17:33:47Z'
KIOTO_RFC_2822 = 'Thursday, 11-Dec-97 17:33:47 UTC'
KIOTO_RFC_3339 = '1997-12-11T17:33:47+00:00'
KIOTO_YEAR_MONTH_DATE = [1997, 12, 11]
KIOTO_TIMESTAMP_SEC = 881861627
KIOTO_TIMESTAMP_MS = KIOTO_TIMESTAMP_SEC * 1e3
KIOTO_DATETIME = datetime.datetime(1997, 12, 11, 17, 33, 47)

KIOTO_IMAP_HEADER = 'Thu, 11 Dec 1997 17:33:47 -0000'
KIOTO_IMAP_HEADER_FIXED_TZ = 'Thu, 11 Dec 1997 17:33:47 -00:00'
KIOTO_IMAP_HEADER_SPURIOUS_TZ = 'Thu, 11 Dec 1997 17:33:47 -42:00'
KIOTO_IMAP_HEADER_SPURIOUS2_TZ = 'Thu, 11 Dec 1997 17:33:47 -42:FF'
KIOTO_IMAP_HEADER_GMT = 'Thu, 11 Dec 1997 17:33:47 (GMT)'
KIOTO_IMAP_HEADER_QUOTED_GMT = 'Thu, 11 Dec 1997 17:33:47 "GMT"'
KIOTO_IMAP_HEADER_QUOTED_0000 = 'Thu, 11 Dec 1997 17:33:47 "-00:00"'

TRACY_CYCLONE = 'Wed, 25 Dec 1974 09:52 +1100'
TRACY_CYCLONE_INVALID_DAY = 'Wen, 25 Dec 1974 09:52 +1100'
TRACY_CYCLONE_TZ = 157157520000

NEW_YEAR_BENGALI = 'Sun, 15 Apr 2015 09:00:00 +05:30'
NEW_YEAR_BENGALI_DASH = 'Sun, 15 Apr 2015 09:00:00 +05-30'
NEW_YEAR_BENGALI_DOT = 'Sun, 15 Apr 2015 09:00:00 +05.30'
NEW_YEAR_BENGALI_EXTRA_PARENT = 'Sun, 15 Apr 2015 09:00:00 +0530 (GMT+05:30)'
NEW_YEAR_BENGALI_TS = 1429068600000

KIOTO_SOUNDCLOUD_FORMATS = [
    "1997/12/11 17:33:47 +0000",
    "1997/12/11 17:33:47 Z",
    "1997-12-11 17:33:47",
    "1997-12-11 17:33:47 Z",
    "1997-12-11 17:33:47 +0000",
]
KIOTO_YOUTUBE = '1997-12-11T17:33:47.000Z'  # TODO handle milliseconds
KIOTO_DROPBOX = 'Thu, 11 Dec 1997 17:33:47 +0000'
KIOTO_DROPBOX_TZ = 'Thu, 11 Dec 1997 17:33:47 Z'


class TestDateExt(unittest.TestCase):
    def test_feeling_lucky(self):
        self.assertEqual(timestamp_ms.feeling_lucky(KIOTO_ISO_8601),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.feeling_lucky(KIOTO_ISO_8601_TZ),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.feeling_lucky(KIOTO_RFC_2822),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.feeling_lucky(KIOTO_RFC_3339),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.feeling_lucky(KIOTO_DATETIME),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.feeling_lucky(KIOTO_IMAP_HEADER),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(
            timestamp_ms.feeling_lucky(KIOTO_IMAP_HEADER_FIXED_TZ),
            KIOTO_TIMESTAMP_MS
        )
        self.assertEqual(timestamp_ms.feeling_lucky(KIOTO_TIMESTAMP_SEC),
                         KIOTO_TIMESTAMP_MS)
        with self.assertRaises(Exception):
            timestamp_ms.feeling_lucky(Exception('invalid obj'))

    def test_dropbox(self):
        """dropbox dates - using formatter

        format: %a, %d %b %Y %H:%M:%S %z
        """
        self._test_format(KIOTO_DROPBOX, KIOTO_DROPBOX_TZ)

    def test_gdrive(self):
        self.assertEqual(
            timestamp_ms.from_str(KIOTO_RFC_3339),
            KIOTO_TIMESTAMP_MS
        )

    def test_gmail(self):
        self.assertEqual(timestamp_ms.from_str(KIOTO_IMAP_HEADER),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.from_str(KIOTO_IMAP_HEADER_FIXED_TZ),
                         KIOTO_TIMESTAMP_MS)
        # timezone information will be deleted
        self.assertEqual(timestamp_ms.from_str(KIOTO_IMAP_HEADER_SPURIOUS_TZ),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.from_str(KIOTO_IMAP_HEADER_GMT),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.from_str(KIOTO_IMAP_HEADER_QUOTED_GMT),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.from_str(KIOTO_IMAP_HEADER_QUOTED_0000),
                         KIOTO_TIMESTAMP_MS)
        # tz is such a mess it is not removed, so dateutil raises
        with self.assertRaises(ValueError):
            timestamp_ms.feeling_lucky(KIOTO_IMAP_HEADER_SPURIOUS2_TZ)

    def test_australian_dates(self):
        self.assertEqual(
            timestamp_ms.from_str(TRACY_CYCLONE),
            TRACY_CYCLONE_TZ
        )
        self.assertEqual(
            timestamp_ms.from_str(TRACY_CYCLONE_INVALID_DAY),
            TRACY_CYCLONE_TZ
        )

    def test_bengali_timezone(self):
        self.assertEqual(
            timestamp_ms.feeling_lucky(NEW_YEAR_BENGALI),
            NEW_YEAR_BENGALI_TS
        )
        self.assertEqual(
            timestamp_ms.feeling_lucky(NEW_YEAR_BENGALI_DASH),
            NEW_YEAR_BENGALI_TS
        )
        self.assertEqual(
            timestamp_ms.feeling_lucky(NEW_YEAR_BENGALI_DOT),
            NEW_YEAR_BENGALI_TS
        )
        self.assertEqual(
            timestamp_ms.feeling_lucky(NEW_YEAR_BENGALI_EXTRA_PARENT),
            NEW_YEAR_BENGALI_TS
        )

    def test_posix_timestamp(self):
        """instagram / evernote / linkedin POSIX timestamps"""
        self.assertEqual(
            timestamp_ms.from_posix_timestamp(KIOTO_TIMESTAMP_SEC),
            KIOTO_TIMESTAMP_MS
        )

    def test_iso_8601_utc_dates(self):
        """box / github / onedrive ISO-8601 UTC dates"""
        self._test_format(KIOTO_ISO_8601, KIOTO_ISO_8601_TZ)

    def test_soundcloud(self):
        self.assertEqual(
            timestamp_ms.from_str(KIOTO_SOUNDCLOUD_FORMATS[0]),
            KIOTO_TIMESTAMP_MS
        )
        self.assertEqual(
            timestamp_ms.from_str(KIOTO_SOUNDCLOUD_FORMATS[1]),
            KIOTO_TIMESTAMP_MS
        )
        self.assertEqual(
            timestamp_ms.from_str(KIOTO_SOUNDCLOUD_FORMATS[2]),
            KIOTO_TIMESTAMP_MS
        )
        self.assertEqual(
            timestamp_ms.from_str(KIOTO_SOUNDCLOUD_FORMATS[3]),
            KIOTO_TIMESTAMP_MS
        )
        self.assertEqual(
            timestamp_ms.from_str(KIOTO_SOUNDCLOUD_FORMATS[4]),
            KIOTO_TIMESTAMP_MS
        )

    def test_twitter(self):
        self.assertEqual(
            timestamp_ms.from_datetime(KIOTO_DATETIME),
            KIOTO_TIMESTAMP_MS
        )

    def test_youtube(self):
        """youtube / trello dates"""
        self.assertEqual(
            timestamp_ms.from_str(KIOTO_YOUTUBE),
            KIOTO_TIMESTAMP_MS
        )

    def test_gcontact(self):
        self.assertEqual(
            timestamp_ms.from_ymd(*KIOTO_YEAR_MONTH_DATE),
            KIOTO_TIMESTAMP_MS - 63227000
        )

    def test_from_now(self):
        self.assertGreater(
            timestamp_ms.now(),
            KIOTO_TIMESTAMP_MS
        )

    def test_ensure_is_number(self):
        now = timestamp_ms.now()
        self.assertTrue(isinstance(now, int))

    def test_invalid_format(self):
        with self.assertRaises(ValueError) as exc:
            timestamp_ms.from_str('1nv4l1d f0rm47')
        self.assertEqual(
            exc.exception.message,
            "Unknown string format: '1nv4l1d f0rm47'"
        )

    def test_invalid_unicode_format(self):
        with self.assertRaises(ValueError) as exc:
            timestamp_ms.from_str(u'1nv4£1Ð ƒ0rm47')
        self.assertEqual(
            exc.exception.message,
            u"Unknown string format: {!r}".format(u'1nv4£1Ð ƒ0rm47')
        )

        with self.assertRaises(ValueError) as exc:
            timestamp_ms.from_str('invalid ƒ0rm47')
        self.assertEqual(
            exc.exception.message,
            u"Unknown string format: "
            u"'invalid \\xc6\\x920rm47'"
        )

    def _test_format(self, format, format_tz):
        self.assertEqual(timestamp_ms.from_str(format),
                         KIOTO_TIMESTAMP_MS)
        self.assertEqual(timestamp_ms.from_str(format_tz),
                         KIOTO_TIMESTAMP_MS)

    def test_simple_date(self):
        kioto_date = datetime.datetime(
            KIOTO_DATETIME.year,
            KIOTO_DATETIME.month,
            KIOTO_DATETIME.day
        )
        kioto_date_str = '{0.year}-{0.month}-{0.day}'.format(kioto_date)
        self.assertEqual(
            timestamp_ms.from_str(kioto_date_str),
            timestamp_ms.from_datetime(kioto_date)
        )


if __name__ == '__main__':
    unittest.main()
