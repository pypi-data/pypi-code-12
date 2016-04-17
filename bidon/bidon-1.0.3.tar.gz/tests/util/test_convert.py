import unittest
from decimal import Decimal
from uuid import UUID, uuid4
from datetime import datetime, timezone, time

import bidon.util.convert as cv


class UtilConvertTestCase(unittest.TestCase):
  def test_identity(self):
    self.assertEqual(cv.identity(5), 5)
    self.assertEqual(cv.identity("18"), "18")
    self.assertEqual(cv.identity(None), None)
    self.assertEqual(cv.identity([1,2,3]), [1,2,3])

  def test_to_int(self):
    self.assertEqual(cv.to_int(3), 3)
    self.assertEqual(cv.to_int("3"), 3)
    self.assertRaises(Exception, lambda: cv.to_int("3.3"))
    self.assertRaises(Exception, lambda: cv.to_int(None))

  def test_to_float(self):
    self.assertEqual(cv.to_float(3.3), 3.3)
    self.assertEqual(cv.to_float("3.3"), 3.3)
    self.assertRaises(Exception, lambda: cv.to_float("3.a3"))
    self.assertRaises(Exception, lambda: cv.to_float(None))

  def test_to_decimal(self):
    self.assertEqual(cv.to_decimal(Decimal(3.4)), Decimal(3.4))
    self.assertEqual(cv.to_decimal(3), Decimal(3))
    self.assertEqual(cv.to_decimal(3.4), Decimal(3.4))
    self.assertEqual(cv.to_decimal("3.4"), Decimal("3.4"))
    self.assertRaises(Exception, lambda: cv.to_decimal("a"))
    self.assertRaises(Exception, lambda: cv.to_decimal(None))

  def test_to_bit(self):
    self.assertEqual(cv.to_bit(0), 0)
    self.assertEqual(cv.to_bit(False), 0)
    self.assertEqual(cv.to_bit(1), 1)
    self.assertEqual(cv.to_bit(True), 1)

  def test_to_bool(self):
    self.assertEqual(cv.to_bit(0), False)
    self.assertEqual(cv.to_bit(False), False)
    self.assertEqual(cv.to_bit(1), True)
    self.assertEqual(cv.to_bit(True), True)

  def test_to_uuid(self):
    u = uuid4()
    self.assertEqual(cv.to_uuid(str(u)), u)
    self.assertEqual(cv.to_uuid(u), u)
    self.assertRaises(Exception, lambda: cv.to_uuid(str(u)[:-1]))
    self.assertRaises(Exception, lambda: cv.to_uuid(None))

  def test_to_compressed_string(self):
    tests = [
      (None, None),
      ("", None),
      ("   ", None),
      ("a", "a"),
      (" a", "a"),
      ("a ", "a"),
      (" a  ", "a"),
      ("a b", "a b"),
      ("a  b c", "a b c"),
      ("  a  b   c d    ", "a b c d")
    ]
    for i, o in tests:
      self.assertEqual(cv.to_compressed_string(i), o)
    self.assertEqual(cv.to_compressed_string("  a  b cd ", 5), "a b c")


  def test_to_now(self):
    start = datetime.now().timestamp()

    self.assertLessEqual(start, cv.to_now(None).timestamp())
    self.assertLessEqual(cv.to_now(None).timestamp(), datetime.now().timestamp())

  def test_to_none(self):
    self.assertIsNone(cv.to_none("ABC"))
    self.assertIsNone(cv.to_none(123))
    self.assertIsNone(cv.to_none(None))

  def test_to_true(self):
    self.assertTrue(cv.to_true("ABC"))
    self.assertTrue(cv.to_true(123))
    self.assertTrue(cv.to_true(None))

  def test_to_false(self):
    self.assertFalse(cv.to_false("ABC"))
    self.assertFalse(cv.to_false(123))
    self.assertFalse(cv.to_false(None))

  def test_to_empty_string(self):
    self.assertEqual(cv.to_empty_string("ABC"), "")
    self.assertEqual(cv.to_empty_string(123), "")
    self.assertEqual(cv.to_empty_string(None), "")

  def test_to_new_uuid(self):
    self.assertIsInstance(cv.to_new_uuid(None), UUID)

  def test_incrementor(self):
    i0 = cv.incrementor()
    self.assertEqual(i0(None), 0)
    self.assertEqual(i0(None), 1)
    i1 = cv.incrementor(start=1, step=10)
    self.assertEqual(i1(None), 1)
    self.assertEqual(i1(None), 11)
    self.assertEqual(i1(None), 21)

  def test_string_trimmer(self):
    st0 = cv.string_trimmer()
    st1 = cv.string_trimmer(5)
    self.assertEqual(st0(" a"), "a")
    self.assertEqual(st0("a "), "a")
    self.assertEqual(st0(" a "), "a")
    self.assertEqual(st1("  abcdef  "), "abcde")

  def test_staic_value(self):
    svs = [None, True, 1, {}]
    inps = ["a", 3, []]
    for sv in svs:
      svfx = cv.static_value(sv)
      for inp in inps:
        self.assertEqual(svfx(inp), sv)

  def test_rounded_decimal(self):
    n = Decimal('3.926')
    conv = cv.rounded_decimal(2)
    self.assertEqual(conv(n), Decimal('3.93'))

  def test_index_resolver(self):
    index = dict(a=1, b=2)
    r1 = cv.index_resolver(index, False)
    r2 = cv.index_resolver(index, True)

    self.assertEqual(r1("a"), 1)
    self.assertEqual(r2("b"), 2)
    self.assertEqual(r1("c"), None)
    with self.assertRaises(KeyError):
      r2("d")

  def test_accept_none_wrapper(self):
    conv = cv.accept_none_wrapper(cv.to_int)
    self.assertEqual(conv(None), None)
    self.assertEqual(conv("3"), 3)
    self.assertEqual(conv(3), 3)

  def test_try_wrapper(self):
    conv = cv.try_wrapper(cv.to_int)
    self.assertEqual(conv("3"), (True, 3))
    self.assertEqual(conv(3), (True, 3))
    self.assertFalse(conv("3.5")[0])
