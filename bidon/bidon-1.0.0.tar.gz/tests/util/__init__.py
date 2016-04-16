import json
import unittest
from datetime import datetime
from collections import namedtuple

import bidon.util as h

from .test_convert import UtilConvertTestCase
from .test_date import UtilDateTestCase
from .test_transform import UtilTransformTestCase


class UtilTestCase(unittest.TestCase):
  def test_pick(self):
    d = dict(a=1, b=2, c=3, d=4)
    self.assertEqual(h.pick(d, ["a", "b"]), dict(a=1, b=2))
    self.assertEqual(h.pick(d, lambda k: k <= "c"), dict(a=1, b=2, c=3))
    self.assertEqual(h.pick(d, ["a", "b"], transform=lambda n: n * 2), dict(a=2, b=4))

  def test_exclude(self):
    d = dict(a=1, b=2, c=3, d=4)
    self.assertEqual(h.exclude(d, ["a", "b"]), dict(c=3, d=4))
    self.assertEqual(h.exclude(d, lambda k: k >= "c"), dict(a=1, b=2))
    self.assertEqual(h.exclude(d, ["a", "b"], transform=lambda n: n * 2), dict(c=6, d=8))

  def test_to_json(self):
    d = dict(a=[1, 2])
    self.assertEqual(h.to_json(d), json.dumps(d, sort_keys=False, indent=None, separators=(",", ":")))
    self.assertEqual(h.to_json(d, True), json.dumps(d, sort_keys=True, indent=2, separators=(", ", ": ")))
    with self.assertRaises(TypeError):
      d = dict(dt=datetime.now())
      h.to_json(d)
    h.register_json_default(lambda o: hasattr(o, "isoformat"), lambda o: o.isoformat())
    self.assertEqual(h.to_json(d), h.to_json(h.pick(d, ["dt"], transform=lambda n: n.isoformat())))

  def test_has_value(self):
    class A(object):
      def __init__(self):
        self.n = 10

    self.assertEqual(h.has_value(A(), "n"), (True, 10))
    self.assertEqual(h.has_value(A(), "d"), (False, None))
    self.assertEqual(h.has_value(dict(n=10), "n"), (True, 10))
    self.assertEqual(h.has_value(dict(v=10), "n"), (False, None))
    self.assertEqual(h.has_value(None, "n"), (False, None))

  def test_get_value(self):
    class A(object):
      def __init__(self):
        self.n = 10

    self.assertEqual(h.get_value(A(), "n"), 10)
    self.assertEqual(h.get_value(A(), "d"), None)
    self.assertEqual(h.get_value(dict(n=10), "n"), 10)
    self.assertEqual(h.get_value(dict(v=10), "n", "hi"), "hi")
    self.assertEqual(h.get_value(dict(v=10), "n", lambda: "lo"), "lo")
    self.assertEqual(h.get_value(None, "n", 42), 42)

  def test_set_value(self):
    class A(object):
      def __init__(self):
        self.n = 10

    a = A()
    b = {}
    c = []
    h.set_value(a, "n", 15)
    self.assertEqual(a.n, 15)
    h.set_value(b, "v", 18)
    self.assertEqual(b["v"], 18)
    self.assertRaises(Exception, lambda: h.set_value(c, "q", 13))

  def test_with_defaults(self):
    def a(b,c,d): return [b,c,d]
    self.assertEqual([None, None, None], h.with_defaults(a, 3))
    self.assertEqual([1, None, None], h.with_defaults(a, 3, [1]))
    self.assertEqual([1, 2, 3], h.with_defaults(a, 3, [1, 2, 3]))

  def test_namedtuple_with_defaults(self):
    nt = namedtuple("Point3d", ["x", "y", "z"])
    self.assertEqual(nt(None, None, None), h.namedtuple_with_defaults(nt))
    self.assertEqual(nt(1, None, None), h.namedtuple_with_defaults(nt, [1]))
    self.assertEqual(nt(1, 2, 3), h.namedtuple_with_defaults(nt, [1, 2, 3]))

  def test_flatten_dict(self):
    self.assertEqual(
      sorted(h.flatten_dict(
        {"a": {"c": 1, "d": 2},
         "b": {"c": 10, "d": 11, "e": 12},
         "c": 20})),
      [(("a", "c"), 1),
       (("a", "d"), 2),
       (("b", "c"), 10),
       (("b", "d"), 11),
       (("b", "e"), 12),
       (("c", ), 20)])
