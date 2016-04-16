import unittest

from bidon.field_mapping import FieldMapping


class FMSource(object):
  def __init__(self, name, age, house):
    self.name = name
    self.age = age
    self.house = house


class FMDest(object):
  def __init__(self, first_name, last_name, age, house_name):
    self.first_name = first_name
    self.last_name = last_name
    self.age = age
    self.house_name = house_name


fn_fm = FieldMapping("name", "first_name", lambda v: v.split(", ")[1])
ln_fm = FieldMapping("name", "last_name", lambda v: v.split(", ")[0])
age_fm = FieldMapping("age")
house_fm = FieldMapping("house", "house_name", lambda v: "{0} House".format(v), False)


class FieldMappingTestCase(unittest.TestCase):
  def test_get_value(self):
    s1 = FMSource("Ravenclaw, Rowena", 40, "Ravenclaw")
    self.assertEqual(fn_fm.get_value(s1), "Rowena")
    self.assertEqual(ln_fm.get_value(s1), "Ravenclaw")
    self.assertEqual(age_fm.get_value(s1), 40)
    self.assertEqual(house_fm.get_value(s1), "Ravenclaw House")
    s2 = { "age": 55 }
    self.assertEqual(age_fm.get_value(s2), 55)
    s3 = { }
    self.assertRaises(Exception, lambda: age_fm.get_value(s3))
    self.assertIsNone(house_fm.get_value(s3))

  def test_transfer(self):
    s1 = FMSource("Gryffindor, Godric", 40, "Gryffindor")
    s2 = dict(name="Gryffindor, Godric", age=40)
    fms = [fn_fm, ln_fm, age_fm, house_fm]

    d1 = FieldMapping.transfer(fms, s1, lambda d: FMDest(**d))
    self.assertEqual(d1.first_name, "Godric")
    self.assertEqual(d1.last_name, "Gryffindor")
    self.assertEqual(d1.age, 40)
    self.assertEqual(d1.house_name, "Gryffindor House")

    d2 = FieldMapping.transfer(fms, s1, dict)
    self.assertEqual(d2, dict(first_name="Godric", last_name="Gryffindor", age=40, house_name="Gryffindor House"))

    d3 = FieldMapping.transfer(fms, s2, lambda x: x)
    self.assertEqual(d3, dict(first_name="Godric", last_name="Gryffindor", age=40, house_name=None))

  def test_transfer_all(self):
    sources = [
      FMSource("McGonagall, Minerva", 40, "Gryffindor"),
      FMSource("Flitwick, Filius", 40, "Ravenclaw"),
      FMSource("Sprout, Pomona", 40, "Hufflepuff"),
      FMSource("Snape, Severus", 40, "Slytherin")
    ]
    fms = [fn_fm, ln_fm, age_fm, house_fm]

    d1 = list(FieldMapping.transfer_all(fms, sources, lambda d: FMDest(**d)))
    self.assertEqual(len(d1), 4)
    self.assertIsInstance(d1[0], FMDest)
    self.assertEqual(d1[0].first_name, "Minerva")

    d2 = list(FieldMapping.transfer_all(fms, sources))
    self.assertEqual(len(d2), 4)
    self.assertIsInstance(d2[0], dict)
    self.assertEqual(d2[-1]["last_name"], "Snape")

    d3 = list(FieldMapping.transfer_all(fms, sources, FieldMapping.get_namedtuple_factory(fms)))
    self.assertEqual(len(d3), 4)
    self.assertEqual(d3[0].first_name, "Minerva")

  def test_get_namedtuple(self):
    fms = [fn_fm, ln_fm, age_fm, house_fm]
    nt = FieldMapping.get_namedtuple(fms)
    for fm in fms:
      self.assertTrue(hasattr(nt, fm.destination_name))

  def test_get_namedtuple_factory(self):
    fms = [fn_fm, ln_fm, age_fm, house_fm]
    ntf = FieldMapping.get_namedtuple_factory(fms)
    nt = ntf(dict(first_name="Vernon", last_name="Dursley", age=35, house_name="Privet Drive"))
    for fm in fms:
      self.assertTrue(hasattr(nt, fm.destination_name))
