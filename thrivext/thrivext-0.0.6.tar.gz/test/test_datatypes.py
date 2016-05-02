import unittest
import thrivext.datatypes as tx_datatypes


class TestDatatypes(unittest.TestCase):
    def test_date_valid(self):
        dt_strings = ["04/21/2016",
                      "04/24/16",
                      "04-24-2016",
                      "04-24-16",
                      "04/1/2016",
                      "04/1/16",
                      "2016/04/24",
                      "2016/04/1",
                      "2016-04-24",
                      "2016-04-1"]

        for dt in dt_strings:
            self.assertTrue(
                isinstance(dt, tx_datatypes.Date),
                "%s is an invalid date" % dt
            )

    def test_date_invalid(self):
        dt_strings = ["04/212/2016",
                      "04/242/16",
                      "04-242-2016",
                      "04/242/2016",
                      "2016-04-a",
                      "2015/02/29"]

        for dt in dt_strings:
            self.assertFalse(
                isinstance(dt, tx_datatypes.Date),
                "%s is a valid date" % dt
            )

    def test_timestamp_valid(self):
        ts_strings = ["2015-11-20 17:03:13",
                      "2015-11-20T17:03:13"]

        for ts in ts_strings:
            self.assertTrue(
                isinstance(ts, tx_datatypes.Timestamp),
                "%s is an invalid timestamp" % ts
            )

    def test_timestamp_invalid(self):
        ts_strings = ["2015-11-20 xx:03:13",
                      "2015-11-20Z17:03:13",
                      "2015-11-20  17:03:13"]

        for ts in ts_strings:
            self.assertFalse(
                isinstance(ts, tx_datatypes.Timestamp),
                "%s is a valid timestamp" % ts
            )

    def test_float_valid(self):
        float_strings = ["25", "25.2", "0.25", "1.0e-5",
                         "-25", "-25.0", "-0.25", "-1.0e-5"]
        for fs in float_strings:
            self.assertTrue(
                isinstance(fs, tx_datatypes.Float),
                "%s is an invalid float" % fs
            )

    def test_float_invalid(self):
        float_strings = ["xxx", "25.a", "a.25"]
        for fs in float_strings:
            self.assertFalse(
                isinstance(fs, tx_datatypes.Float),
                "%s is a valid float" % fs
            )

    def test_integer_valid(self):
        int_strings = ["0", "001", "100", "-0", "-200", "-001"]
        for istr in int_strings:
            self.assertTrue(
                isinstance(istr, tx_datatypes.Integer),
                "%s is an invalid integer" % istr
            )

    def test_integer_invalid(self):
        int_strings = ["a", "0.01"]
        for istr in int_strings:
            self.assertFalse(
                isinstance(istr, tx_datatypes.Integer),
                "%s is a valid integer" % istr
            )

    def test_boolean_valid(self):
        bool_strings = ["TRUE", "true", "t", "T", "1", "y", "yes", "YES",
                        "FALSE", "false", "f", "F", "0", "n", "no", "NO"]
        for bs in bool_strings:
            self.assertTrue(
                isinstance(bs, tx_datatypes.Boolean),
                "%s is an invalid Boolean" % bs
            )

    def test_boolean_invalid(self):
        bool_strings = ["yeah", "sure", "you got it",
                        "nah", "hell no", "yeah right"]
        for bs in bool_strings:
            self.assertFalse(
                isinstance(bs, tx_datatypes.Boolean),
                "%s is an invalid Boolean" % bs
            )


if __name__ == "__main__":
    unittest.main()

