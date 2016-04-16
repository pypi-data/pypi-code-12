import unittest

from bidon import json_patch as jp


class JSONPatchTestCase(unittest.TestCase):
  def setUp(self):
    self.document = {
      "name": "Trey",
      "computers": ["13\" macbook", "15\" macbook pro", "iPad 1"],
      "age": 31,
      "spouse": {
        "name": "Julie",
        "age": 29,
        "computers": ["13\" macbook pro", "iPhone 6"],
      },
      "children": ["Asher"],
      "path/test": {
        "goes~to": "o7911"
      }
    }

  def apply_patch(self, patch):
    jp.apply_patch(self.document, patch)
    return self.document

  def test_path_escapes(self):
    r, i = jp.resolve_path(self.document, "/path~1test/goes~0to")
    self.assertEqual(r[i], "o7911")

  def test_add(self):
    patch = jp.Patch(op="add", path="/eye_color", value="blue")
    self.assertEqual(self.apply_patch(patch)["eye_color"], "blue")

    patch = jp.Patch(op="add", path="/spouse/eye_color", value="brown")
    self.assertEqual(self.apply_patch(patch)["spouse"]["eye_color"], "brown")

    patch = jp.Patch(op="add", path="/computers/2", value="iPhone 5")
    self.assertEqual(self.apply_patch(patch)["computers"][2], "iPhone 5")

    patch = jp.Patch(op="add", path="/computers/", value="iPhone 6")
    self.assertEqual(self.apply_patch(patch)["computers"][-1], "iPhone 6")

    patch = jp.Patch(op="add", path="/computers/~", value="iPhone 6 Plus")
    self.assertEqual(self.apply_patch(patch)["computers"][-1], "iPhone 6 Plus")

    with self.assertRaises(Exception):
      self.apply_patch(jp.Patch(op="add", path="/name", value=None))

  def test_remove(self):
    patch = jp.Patch(op="remove", path="/age")
    self.assertTrue("age" not in self.apply_patch(patch))

    patch = jp.Patch(op="remove", path="/computers/0")
    pv = self.document["computers"][0]
    self.assertNotEqual(self.apply_patch(patch)["computers"][0], pv)

    with self.assertRaises(Exception):
      self.apply_patch(jp.Patch(op="remove", path="eye_color"))

  def test_replace(self):
    patch = jp.Patch(op="replace", path="/age", value=32)
    self.assertEqual(self.apply_patch(patch)["age"], 32)

    with self.assertRaises(Exception):
      self.apply_patch(jp.Patch(op="replace", path="/eye_color", value="green"))

  def test_merge(self):
    patch = jp.Patch(op="merge", path="/spouse", value=dict(age=30, name="Juliana", hair_length="long"))
    self.apply_patch(patch)
    s = self.document["spouse"]
    self.assertEqual(s["age"], 30)
    self.assertEqual(s["name"], "Juliana")
    self.assertEqual(s["hair_length"], "long")

  def test_copy(self):
    patch = jp.Patch(op="copy", src="/computers", path="/spouse/computers")
    self.apply_patch(patch)
    self.assertEqual(self.document["computers"], self.document["spouse"]["computers"])

  def test_move(self):
    patch = jp.Patch(op="move", src="/children", path="/spouse/children")
    mv = self.document["children"]
    self.assertEqual(self.apply_patch(patch)["spouse"]["children"], mv)

  def test_test(self):
    d = self.document
    self.assertTrue(jp.apply_patch(d, jp.Patch(op="test", path="/age")))
    self.assertTrue(jp.apply_patch(d, jp.Patch(op="test", path="/age", value=31)))
    self.assertFalse(jp.apply_patch(d, jp.Patch(op="test", path="/age", value=32)))
    self.assertFalse(jp.apply_patch(d, jp.Patch(op="test", path="/hamburger_count")))
    self.assertFalse(jp.apply_patch(d, jp.Patch(op="test", path="/hamburger_count", value="the, all of")))

  def test_set_remove(self):
    v = "13\" macbook pro"
    patch = jp.Patch(op="setremove", path="/spouse/computers", value=v)
    self.assertTrue(v in self.document["spouse"]["computers"])
    self.assertFalse(v in self.apply_patch(patch)["spouse"]["computers"])

  def test_set_add(self):
    v = "iPad Air"
    patch = jp.Patch(op="setadd", path="/computers", value=v)
    self.assertFalse(v in self.document["computers"])
    self.assertTrue(self.apply_patch(patch)["computers"].count(v) == 1)
    # Adding the same item multiple times to a set has no effect
    self.assertTrue(self.apply_patch(patch)["computers"].count(v) == 1)

  def test_find(self):
    self.assertEqual(jp.find(self.document, "/spouse/name"), "Julie")
    self.assertEqual(jp.find(self.document, "/spouse/computers/1"), "iPhone 6")

  def test_find_all(self):
    doc = dict(
      person=dict(
        name="Trey",
        things=[
          dict(id=1, name="One"),
          dict(id=2, name="Two")
        ]))
    self.assertEqual(set(jp.find_all(doc, "/person/things/*/name")), {"One", "Two"})
