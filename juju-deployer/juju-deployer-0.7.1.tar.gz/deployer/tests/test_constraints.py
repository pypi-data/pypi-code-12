from deployer.service import Service
from .base import Base
from ..utils import parse_constraints


class ConstraintsTest(Base):

    def test_constraints(self):
        data = {
            'branch': 'lp:precise/mysql',
            'constraints': "instance-type=m1.small",
        }
        s = Service('db', data)
        self.assertEquals(s.constraints, "instance-type=m1.small")
        data = {
            'branch': 'lp:precise/mysql',
            'constraints': "cpu-cores=4 mem=2048M root-disk=10G",
        }
        s = Service('db', data)
        c = parse_constraints(s.constraints)
        self.assertEquals(s.constraints, "cpu-cores=4 mem=2048M root-disk=10G")
        self.assertEqual(c['cpu-cores'], 4)
        self.assertEqual(c['mem'], 2048)
        self.assertEqual(c['root-disk'], 10 * 1024)

    def test_constraints_none(self):
        # If passed None, parse_constraints returns None.
        result = parse_constraints(None)
        self.assertIsNone(result)

    def test_constraints_dict(self):
        # The function can also accept a dict.
        value = {
            'mem': '1G',
            'cpu-cores': '5',
            'root-disk': '100',
        }
        result = parse_constraints(value)
        self.assertEqual(result['cpu-cores'], 5)
        self.assertEqual(result['mem'], 1024)
        self.assertEqual(result['root-disk'], 100)

    def test_constraints_accepts_no_spec(self):
        value = {
            'mem': '1',
            'root-disk': '10',
        }
        result = parse_constraints(value)
        self.assertEqual(result['mem'], 1)
        self.assertEqual(result['root-disk'], 10)

    def test_constraints_accept_M(self):
        value = {
            'mem': '1M',
            'root-disk': '10M',
        }
        mult = 1
        result = parse_constraints(value)
        self.assertEqual(result['mem'], 1 * mult)
        self.assertEqual(result['root-disk'], 10 * mult)

    def test_constraints_accept_G(self):
        value = {
            'mem': '1G',
            'root-disk': '10G',
        }
        result = parse_constraints(value)
        mult = 1024
        self.assertEqual(result['mem'], 1 * mult)
        self.assertEqual(result['root-disk'], 10 * mult)

    def test_constraints_accept_T(self):
        value = {
            'mem': '1T',
            'root-disk': '10T',
        }
        result = parse_constraints(value)
        mult = 1024 * 1024
        self.assertEqual(result['mem'], 1 * mult)
        self.assertEqual(result['root-disk'], 10 * mult)

    def test_constraints_accept_P(self):
        value = {
            'mem': '1P',
            'root-disk': '10P',
        }
        result = parse_constraints(value)
        mult = 1024 * 1024 * 1024
        self.assertEqual(result['mem'], 1 * mult)
        self.assertEqual(result['root-disk'], 10 * mult)

    def test_constraints_reject_other_sizes(self):
        value = {
            'mem': '1E',
        }
        with self.assertRaises(ValueError) as exc:
            result = parse_constraints(value)
        self.assertEqual('Constraint mem has invalid value 1E',
                         exc.exception.message)

    def test_other_numeric_constraints_have_no_units(self):
        # If any other numeric constraint gets a units specifier an error is
        # raised.
        keys = ['cpu-power', 'cpu-cores']
        for k in keys:
            value = {
                k: '1T',
            }
            with self.assertRaises(ValueError) as exc:
                parse_constraints(value)
            self.assertEqual('Constraint {} has invalid value 1T'.format(k),
                         exc.exception.message)

    def test_non_numerics_are_not_converted(self):
        # Constraints that expect strings are not affected by the parsing.
        keys = ['arch', 'container']
        for k in keys:
            value = {
                k: '1T',
            }
            result = parse_constraints(value)
            self.assertEqual(result[k], '1T')

    def test_tags(self):
        # Tags are provided as a list of strings.
        constraints = parse_constraints({'tags': 'foo,bar'})
        self.assertEqual({'tags': ['foo', 'bar']}, constraints)

    def test_single_tag(self):
        # A single tag is converted to a list.
        constraints = parse_constraints({'tags': 'foo'})
        self.assertEqual({'tags': ['foo']}, constraints)
