import unittest

from bidon.configuration import Configuration

class ConfigurationTestCase(unittest.TestCase):
  def test_configuration(self):
    c = Configuration(name="Trey", age=32, kid_count=2)
    c.update(name="Trey Cucco", spouse="Julie")
    self.assertFalse(c.is_frozen)
    c.freeze()
    self.assertEqual(c.name, "Trey Cucco")
    self.assertEqual(c.age, 32)
    self.assertEqual(c.kid_count, 2)
    self.assertEqual(c.spouse, "Julie")

    with self.assertRaises(Exception):
      c.name = "Trey"
    with self.assertRaises(Exception):
      c.last_name = "Cucco"
    with self.assertRaises(Exception):
      c.update(siblings=1)

