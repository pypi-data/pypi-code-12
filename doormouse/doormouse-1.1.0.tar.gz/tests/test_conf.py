#!/usr/bin/env python
import unittest
from doormouse import conf


class TestConf(unittest.TestCase):
    """Tests parsing the configuration file."""
    def test_empty(self):
        """Tests parsing an empty conf file."""
        data = ""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """ {} """
        with self.assertRaises(ValueError):
            conf.parse(data)

    def test_bad_ca(self):
        """Tests parsing a conf file with bad CA values."""
        # no list of CAs
        data = """ { "ca": "" } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # list of CAs is empty
        data = """ { "ca": [] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # CA is not a list
        data = """ { "ca": "a" } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """ { "ca": {} } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # missing nickname
        data = """ { "ca": [ {"cn": "Example"} ] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # missing common name
        data = """ { "ca": [ {"nickname": "example"} ] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

    def test_bad_nickname(self):
        """Tests parsing a conf file with bad CA nicknames."""
        data = """ { "ca": [ {"nickname": "%s", "cn": "foo"} ] } """
        bad = ["space space", "punct!", "punct%", "punct{", "punct'", "punct\"", "punct-"]

        # __tracked__ is reserved
        bad.append("__tracked__")

        for b in bad:
            with self.assertRaises(ValueError):
                conf.parse(data % b)

        # test a full good name for good measure
        good = "abcdefABCDEF0123456789_"
        conf.parse(data % good)  # should not raise exception

    def test_single_ca(self):
        """Tests parsing a conf file with a single CA and default values."""
        # just the required data
        data = """ { "ca": [ {"nickname": "example", "cn": "Example CA"} ] } """
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("example", cnf["ca"][0]["nickname"])
        self.assertEqual("Example CA", cnf["ca"][0]["cn"])

        # required with org data
        data = """ { "ca": [ {"nickname": "example", "cn": "Example CA", "o": "Example Inc"} ] } """
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("example", cnf["ca"][0]["nickname"])
        self.assertEqual("Example CA", cnf["ca"][0]["cn"])
        self.assertEqual("Example Inc", cnf["ca"][0]["o"])

        # required with org unit data
        data = """ { "ca": [ {"nickname": "example", "cn": "Example CA", "ou": "IT Services"} ] } """
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("example", cnf["ca"][0]["nickname"])
        self.assertEqual("Example CA", cnf["ca"][0]["cn"])
        self.assertEqual("IT Services", cnf["ca"][0]["ou"])

        # all data
        data = """ { "ca": [ {"nickname": "example", "cn": "Example CA", "o": "Example", "ou": "IT Services"} ] } """
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("example", cnf["ca"][0]["nickname"])
        self.assertEqual("Example CA", cnf["ca"][0]["cn"])
        self.assertEqual("Example", cnf["ca"][0]["o"])
        self.assertEqual("IT Services", cnf["ca"][0]["ou"])

    def test_multiple_ca(self):
        """Tests parsing a conf file with multiple CAs."""
        data = """
        {
            "ca": [
                {"nickname": "A0", "cn": "B0"},
                {"nickname": "A1", "cn": "B1", "o": "C1"},
                {"nickname": "A2", "cn": "B2", "ou": "C2"},
                {"nickname": "A3", "cn": "B3", "o": "C3", "ou": "D3"}
            ]
        }
        """
        cnf = conf.parse(data)
        self.assertEqual(4, len(cnf["ca"]))
        self.assertEqual("A0", cnf["ca"][0]["nickname"])
        self.assertEqual("B0", cnf["ca"][0]["cn"])
        self.assertEqual("A1", cnf["ca"][1]["nickname"])
        self.assertEqual("B1", cnf["ca"][1]["cn"])
        self.assertEqual("C1", cnf["ca"][1]["o"])
        self.assertEqual("A2", cnf["ca"][2]["nickname"])
        self.assertEqual("B2", cnf["ca"][2]["cn"])
        self.assertEqual("C2", cnf["ca"][2]["ou"])
        self.assertEqual("A3", cnf["ca"][3]["nickname"])
        self.assertEqual("B3", cnf["ca"][3]["cn"])
        self.assertEqual("C3", cnf["ca"][3]["o"])
        self.assertEqual("D3", cnf["ca"][3]["ou"])

    def test_bad_subca(self):
        """Tests parsing a conf file with bad Sub CA values."""
        # an empty subca should not raise an error but should not be present in the conf
        data = """ { "ca": [ {"nickname": "root", "cn": "RootCA", "subca": [%s] } ] } """
        cnf = conf.parse(data % "")
        self.assertEqual("root", cnf["ca"][0]["nickname"])
        self.assertEqual("RootCA", cnf["ca"][0]["cn"])
        self.assertNotIn("subca", cnf["ca"][0])

        # subca is not a list
        data = """ { "ca": [ {"nickname": "root", "cn": "RootCA", "subca": "" } ] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """ { "ca": [ {"nickname": "root", "cn": "RootCA", "subca": "abc" } ] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """ { "ca": [ {"nickname": "root", "cn": "RootCA", "subca": {} } ] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # missing nickname
        data = """ { "ca": [ {"nickname": "root", "cn": "RootCA", "subca": [ {"cn": "a"}] } ] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # missing common name
        data = """ { "ca": [ {"nickname": "root", "cn": "RootCA", "subca": [ {"nickname": "a"}] } ] } """
        with self.assertRaises(ValueError):
            conf.parse(data)

    def test_single_subca(self):
        """Tests parsing a conf file with a single subca."""
        data = """ { "ca": [ {"nickname": "root", "cn": "RootCA", "subca": [%s] } ] } """

        # just the required data
        subs = """ { "nickname": "sub", "cn": "SubCA"} """
        cnf = conf.parse(data % subs)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("root", cnf["ca"][0]["nickname"])
        self.assertEqual("RootCA", cnf["ca"][0]["cn"])
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual("sub", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("SubCA", cnf["ca"][0]["subca"][0]["cn"])

        # required with org data
        subs = """ { "nickname": "sub", "cn": "SubCA", "o": "A" } """
        cnf = conf.parse(data % subs)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("root", cnf["ca"][0]["nickname"])
        self.assertEqual("RootCA", cnf["ca"][0]["cn"])
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual("sub", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("SubCA", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("A", cnf["ca"][0]["subca"][0]["o"])

        # required with org unit data
        subs = """ { "nickname": "sub", "cn": "SubCA", "ou": "A" } """
        cnf = conf.parse(data % subs)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("root", cnf["ca"][0]["nickname"])
        self.assertEqual("RootCA", cnf["ca"][0]["cn"])
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual("sub", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("SubCA", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("A", cnf["ca"][0]["subca"][0]["ou"])

        # all data
        subs = """ { "nickname": "sub", "cn": "SubCA", "o": "A", "ou": "B" } """
        cnf = conf.parse(data % subs)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("root", cnf["ca"][0]["nickname"])
        self.assertEqual("RootCA", cnf["ca"][0]["cn"])
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual("sub", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("SubCA", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("A", cnf["ca"][0]["subca"][0]["o"])
        self.assertEqual("B", cnf["ca"][0]["subca"][0]["ou"])

    def test_multiple_subca(self):
        """Tests parsing a conf file with multiple Sub CAs."""
        # one CA with multiple Sub CAs
        data = """
        {
            "ca": [ {"nickname": "X", "cn": "Y", "subca": [
                {"nickname": "A0", "cn": "B0" },
                {"nickname": "A1", "cn": "B1", "o": "C1" },
                {"nickname": "A2", "cn": "B2", "ou": "C2" },
                {"nickname": "A3", "cn": "B3", "o": "C3", "ou": "D3"}
            ]}]
        }
        """
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual("X", cnf["ca"][0]["nickname"])
        self.assertEqual("Y", cnf["ca"][0]["cn"])
        self.assertEqual(4, len(cnf["ca"][0]["subca"]))
        self.assertEqual("A0", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("B0", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("A1", cnf["ca"][0]["subca"][1]["nickname"])
        self.assertEqual("B1", cnf["ca"][0]["subca"][1]["cn"])
        self.assertEqual("C1", cnf["ca"][0]["subca"][1]["o"])
        self.assertEqual("A2", cnf["ca"][0]["subca"][2]["nickname"])
        self.assertEqual("B2", cnf["ca"][0]["subca"][2]["cn"])
        self.assertEqual("C2", cnf["ca"][0]["subca"][2]["ou"])
        self.assertEqual("A3", cnf["ca"][0]["subca"][3]["nickname"])
        self.assertEqual("B3", cnf["ca"][0]["subca"][3]["cn"])
        self.assertEqual("C3", cnf["ca"][0]["subca"][3]["o"])
        self.assertEqual("D3", cnf["ca"][0]["subca"][3]["ou"])

        # multiple CA with multiple Subs
        data = """
        {
            "ca": [
                {"nickname": "X", "cn": "Y", "subca": [
                    {"nickname": "A0", "cn": "B0" },
                    {"nickname": "A1", "cn": "B1", "o": "C1" }
                ]},
                {"nickname": "Q", "cn": "R", "subca": [
                    {"nickname": "M0", "cn": "M1"}
                ]},
                {"nickname": "E", "cn": "F"}
            ]
        }
        """
        cnf = conf.parse(data)
        self.assertEqual(3, len(cnf["ca"]))
        self.assertEqual("X", cnf["ca"][0]["nickname"])
        self.assertEqual("Y", cnf["ca"][0]["cn"])
        self.assertEqual(2, len(cnf["ca"][0]["subca"]))
        self.assertEqual("A0", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("B0", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("A1", cnf["ca"][0]["subca"][1]["nickname"])
        self.assertEqual("B1", cnf["ca"][0]["subca"][1]["cn"])
        self.assertEqual("C1", cnf["ca"][0]["subca"][1]["o"])

        self.assertEqual(1, len(cnf["ca"][1]["subca"]))
        self.assertEqual("Q", cnf["ca"][1]["nickname"])
        self.assertEqual("R", cnf["ca"][1]["cn"])
        self.assertEqual("M0", cnf["ca"][1]["subca"][0]["nickname"])
        self.assertEqual("M1", cnf["ca"][1]["subca"][0]["cn"])

        self.assertEqual("E", cnf["ca"][2]["nickname"])
        self.assertEqual("F", cnf["ca"][2]["cn"])
        self.assertNotIn("subca", cnf["ca"][2])

    def test_bad_cert(self):
        """Tests parsing a conf file with bad cert values."""
        # test entities as elements of a CA and Sub CA
        data_top = """{"ca": [{"nickname": "A", "cn": "B", "cert": [%s]}]}"""
        data_sub = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "cert": [%s]}]}]}"""

        # an empty cert should not raise an error but should not be present in the conf
        cnf = conf.parse(data_top % "")
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertNotIn("cert", cnf["ca"][0])

        cnf = conf.parse(data_sub % "")
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertNotIn("cert", cnf["ca"][0]["subca"][0])

        # cert is not a list
        data_bad = """{"ca": [{"nickname": "A", "cn": "B", "cert": ""}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data_bad)

        data_bad = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "cert": ""}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data_bad)

        data_bad = """{"ca": [{"nickname": "A", "cn": "B", "cert": "abc"}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data_bad)

        data_bad = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "cert": "abc"}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data_bad)

        data_bad = """{"ca": [{"nickname": "A", "cn": "B", "cert": {}}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data_bad)

        data_bad = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "cert": {}}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data_bad)

        # missing nickname
        with self.assertRaises(ValueError):
            conf.parse(data_top % "{}")

        with self.assertRaises(ValueError):
            conf.parse(data_sub % "{}")

    def test_single_cert(self):
        """Tests parsing a conf file with a single cert."""

        # test entities as elements of a CA and Sub CA
        data_top = """{"ca": [{"nickname": "A", "cn": "B", "cert": [%s]}]}"""
        data_sub = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "cert": [%s]}]}]}"""

        # just the required data
        ent = """ { "nickname": "Z"} """
        cnf = conf.parse(data_top % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertNotIn("subca", cnf["ca"][0])
        self.assertEqual(1, len(cnf["ca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["cert"][0]["nickname"])

        cnf = conf.parse(data_sub % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["subca"][0]["cert"][0]["nickname"])

        # required with org data
        ent = """ { "nickname": "Z", "o": "X"} """
        cnf = conf.parse(data_top % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertNotIn("subca", cnf["ca"][0])
        self.assertEqual(1, len(cnf["ca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual("X", cnf["ca"][0]["cert"][0]["o"])

        cnf = conf.parse(data_sub % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["subca"][0]["cert"][0]["nickname"])
        self.assertEqual("X", cnf["ca"][0]["subca"][0]["cert"][0]["o"])

        # required with org unit data
        ent = """ { "nickname": "Z", "ou": "X"} """
        cnf = conf.parse(data_top % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertNotIn("subca", cnf["ca"][0])
        self.assertEqual(1, len(cnf["ca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual("X", cnf["ca"][0]["cert"][0]["ou"])

        cnf = conf.parse(data_sub % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["subca"][0]["cert"][0]["nickname"])
        self.assertEqual("X", cnf["ca"][0]["subca"][0]["cert"][0]["ou"])

        # all data
        ent = """ { "nickname": "Z", "o": "X", "ou": "Y"} """
        cnf = conf.parse(data_top % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertNotIn("subca", cnf["ca"][0])
        self.assertEqual(1, len(cnf["ca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual("X", cnf["ca"][0]["cert"][0]["o"])
        self.assertEqual("Y", cnf["ca"][0]["cert"][0]["ou"])

        cnf = conf.parse(data_sub % ent)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"][0]["cert"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("Z", cnf["ca"][0]["subca"][0]["cert"][0]["nickname"])
        self.assertEqual("X", cnf["ca"][0]["subca"][0]["cert"][0]["o"])
        self.assertEqual("Y", cnf["ca"][0]["subca"][0]["cert"][0]["ou"])

    def test_multiple_entities(self):
        """Tests parsing a conf file with multiple entities."""
        # single ca with multiple entities
        data = """{"ca": [{"nickname": "A0", "cn": "A1", "cert": [
            {"nickname": "B"}, {"nickname": "C"}, {"nickname": "D"} ] } ] }"""
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertNotIn("subca", cnf["ca"][0])
        self.assertEqual(3, len(cnf["ca"][0]["cert"]))
        self.assertEqual("A0", cnf["ca"][0]["nickname"])
        self.assertEqual("A1", cnf["ca"][0]["cn"])
        self.assertEqual("B", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual("C", cnf["ca"][0]["cert"][1]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["cert"][2]["nickname"])

        # single subca with multiple entities
        data = """{"ca": [{"nickname": "A0", "cn": "A1", "subca": [ {"nickname": "B0", "cn": "B1", "cert": [
            {"nickname": "B"}, {"nickname": "C"}, {"nickname": "D"} ] } ] } ] }"""
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"]))
        self.assertEqual(3, len(cnf["ca"][0]["subca"][0]["cert"]))
        self.assertEqual("A0", cnf["ca"][0]["nickname"])
        self.assertEqual("A1", cnf["ca"][0]["cn"])
        self.assertEqual("B0", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("B1", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("B", cnf["ca"][0]["subca"][0]["cert"][0]["nickname"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["cert"][1]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cert"][2]["nickname"])

        # multiple ca with multiple entities
        data = """
            {"ca": [
                {"nickname": "A0", "cn": "A1", "cert": [{"nickname": "M"}]},
                {"nickname": "B0", "cn": "B1", "cert": [{"nickname": "N"}, {"nickname": "O"}]},
                {"nickname": "C0", "cn": "C1", "cert": [{"nickname": "P"}, {"nickname": "Q"}, {"nickname": "R"}]}
            ]}
        """
        cnf = conf.parse(data)
        self.assertEqual(3, len(cnf["ca"]))
        self.assertEqual(1, len(cnf["ca"][0]["cert"]))
        self.assertEqual("A0", cnf["ca"][0]["nickname"])
        self.assertEqual("A1", cnf["ca"][0]["cn"])
        self.assertEqual("M", cnf["ca"][0]["cert"][0]["nickname"])

        self.assertEqual(2, len(cnf["ca"][1]["cert"]))
        self.assertEqual("B0", cnf["ca"][1]["nickname"])
        self.assertEqual("B1", cnf["ca"][1]["cn"])
        self.assertEqual("N", cnf["ca"][1]["cert"][0]["nickname"])
        self.assertEqual("O", cnf["ca"][1]["cert"][1]["nickname"])

        self.assertEqual(3, len(cnf["ca"][2]["cert"]))
        self.assertEqual("C0", cnf["ca"][2]["nickname"])
        self.assertEqual("C1", cnf["ca"][2]["cn"])
        self.assertEqual("P", cnf["ca"][2]["cert"][0]["nickname"])
        self.assertEqual("Q", cnf["ca"][2]["cert"][1]["nickname"])
        self.assertEqual("R", cnf["ca"][2]["cert"][2]["nickname"])

        # multiple subca with multiple entities
        data = """
            {"ca": [{"nickname": "A", "cn": "B", "subca": [
                {"nickname": "A0", "cn": "A1", "cert": [{"nickname": "A2"}, {"nickname": "A3"}, {"nickname": "A4"}]},
                {"nickname": "B0", "cn": "B1", "cert": [{"nickname": "B2"}, {"nickname": "B3"}]},
                {"nickname": "C0", "cn": "C1", "cert": [{"nickname": "C2"}]},
                {"nickname": "D0", "cn": "D1"}
            ]}]}
        """
        cnf = conf.parse(data)
        self.assertEqual(1, len(cnf["ca"]))
        self.assertEqual(4, len(cnf["ca"][0]["subca"]))
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])

        self.assertEqual(3, len(cnf["ca"][0]["subca"][0]["cert"]))
        self.assertEqual("A0", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("A1", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("A2", cnf["ca"][0]["subca"][0]["cert"][0]["nickname"])
        self.assertEqual("A3", cnf["ca"][0]["subca"][0]["cert"][1]["nickname"])
        self.assertEqual("A4", cnf["ca"][0]["subca"][0]["cert"][2]["nickname"])

        self.assertEqual(2, len(cnf["ca"][0]["subca"][1]["cert"]))
        self.assertEqual("B0", cnf["ca"][0]["subca"][1]["nickname"])
        self.assertEqual("B1", cnf["ca"][0]["subca"][1]["cn"])
        self.assertEqual("B2", cnf["ca"][0]["subca"][1]["cert"][0]["nickname"])
        self.assertEqual("B3", cnf["ca"][0]["subca"][1]["cert"][1]["nickname"])

        self.assertEqual(1, len(cnf["ca"][0]["subca"][2]["cert"]))
        self.assertEqual("C0", cnf["ca"][0]["subca"][2]["nickname"])
        self.assertEqual("C1", cnf["ca"][0]["subca"][2]["cn"])
        self.assertEqual("C2", cnf["ca"][0]["subca"][2]["cert"][0]["nickname"])

        self.assertNotIn("cert", cnf["ca"][0]["subca"][3])
        self.assertEqual("D0", cnf["ca"][0]["subca"][3]["nickname"])
        self.assertEqual("D1", cnf["ca"][0]["subca"][3]["cn"])

        # multiple ca, subca, entities all jumbled up
        data = """{"ca": [
            {"nickname": "A0", "cn": "Z",
                "subca": [
                    {"nickname": "A1", "cn": "Z", "cert": [{"nickname": "A2"}, {"nickname": "A3"}]},
                    {"nickname": "A4", "cn": "Z", "cert": [{"nickname": "A5"}]},
                    {"nickname": "A6", "cn": "Z"}
                ],
                "cert": [{"nickname": "A7"}]
            },
            {"nickname": "B0", "cn": "Z", "cert": [{"nickname": "B1"}, {"nickname": "B2"}]},
            {"nickname": "C0", "cn": "Z",
                "subca": [
                    {"nickname": "C1", "cn": "Z", "cert": [{"nickname": "C2"}, {"nickname": "C3"}]},
                    {"nickname": "C4", "cn": "Z"}
                ]
            },
            {"nickname": "D0", "cn": "Z"}
        ]}"""
        cnf = conf.parse(data)
        self.assertEqual(4, len(cnf["ca"]))

        # ca 0
        self.assertEqual(3, len(cnf["ca"][0]["subca"]))
        self.assertEqual(2, len(cnf["ca"][0]["subca"][0]["cert"]))
        self.assertEqual(1, len(cnf["ca"][0]["subca"][1]["cert"]))
        self.assertNotIn("cert", cnf["ca"][0]["subca"][2])
        self.assertEqual(1, len(cnf["ca"][0]["cert"]))

        self.assertEqual("A0", cnf["ca"][0]["nickname"])
        self.assertEqual("Z", cnf["ca"][0]["cn"])
        self.assertEqual("A1", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("Z", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual("A2", cnf["ca"][0]["subca"][0]["cert"][0]["nickname"])
        self.assertEqual("A3", cnf["ca"][0]["subca"][0]["cert"][1]["nickname"])

        self.assertEqual("A4", cnf["ca"][0]["subca"][1]["nickname"])
        self.assertEqual("Z", cnf["ca"][0]["subca"][1]["cn"])
        self.assertEqual("A5", cnf["ca"][0]["subca"][1]["cert"][0]["nickname"])

        self.assertEqual("A6", cnf["ca"][0]["subca"][2]["nickname"])
        self.assertEqual("Z", cnf["ca"][0]["subca"][2]["cn"])

        self.assertEqual("A7", cnf["ca"][0]["cert"][0]["nickname"])

        # ca 1
        self.assertNotIn("subca", cnf["ca"][1])
        self.assertEqual(2, len(cnf["ca"][1]["cert"]))
        self.assertEqual("B0", cnf["ca"][1]["nickname"])
        self.assertEqual("Z", cnf["ca"][1]["cn"])
        self.assertEqual("B1", cnf["ca"][1]["cert"][0]["nickname"])
        self.assertEqual("B2", cnf["ca"][1]["cert"][1]["nickname"])

        # ca 2
        self.assertEqual(2, len(cnf["ca"][2]["subca"]))
        self.assertNotIn("cert", cnf["ca"][2])
        self.assertEqual(2, len(cnf["ca"][2]["subca"][0]["cert"]))
        self.assertNotIn("cert", cnf["ca"][2]["subca"][1])

        self.assertEqual("C0", cnf["ca"][2]["nickname"])
        self.assertEqual("Z", cnf["ca"][2]["cn"])
        self.assertEqual("C1", cnf["ca"][2]["subca"][0]["nickname"])
        self.assertEqual("Z", cnf["ca"][2]["subca"][0]["cn"])
        self.assertEqual("C2", cnf["ca"][2]["subca"][0]["cert"][0]["nickname"])
        self.assertEqual("C3", cnf["ca"][2]["subca"][0]["cert"][1]["nickname"])
        self.assertEqual("C4", cnf["ca"][2]["subca"][1]["nickname"])
        self.assertEqual("Z", cnf["ca"][2]["subca"][1]["cn"])

        # ca 3
        self.assertNotIn("subca", cnf["ca"][3])
        self.assertNotIn("cert", cnf["ca"][3])
        self.assertEqual("D0", cnf["ca"][3]["nickname"])
        self.assertEqual("Z", cnf["ca"][3]["cn"])

    def test_unique_nicknames(self):
        """Tests parsing a conf file that does not have unique nicknames."""
        # CAs have clashing nicknames
        data = """
            {"ca": [
                {"nickname": "A", "cn": "CN0"},
                {"nickname": "A", "cn": "CN1"}
            ]}
        """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # CA and a direct Sub CA have clashing nicknames
        data = """{"ca": [{"nickname": "A", "cn": "CN0", "subca": [{"nickname": "A", "cn": "SN0"}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # CA and a Sub CA from another CA have clashing nicknames
        data = """
            {"ca": [
                {"nickname": "A", "cn": "CN0", "subca": [{"nickname": "AA, "cn": "SN0"}]},
                {"nickname": "B", "cn": "CN1", "subca": [{"nickname": "A, "cn": "SN1"}]}
            ]}
        """
        with self.assertRaises(ValueError):
            conf.parse(data)

        # CA and cert have clashing nicknames
        data = """ {"ca": [ {"nickname": "A", "cn": "B", "cert": [ {"nickname": "A"} ] } ] }"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # entities have clashing nicknames
        data = """ {"ca": [ {"nickname": "A0", "cn": "A1", "cert": [ {"nickname": "B"}, {"nickname": "B"} ] } ] }"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # cert and sub ca have clashing nicknames
        data = """ {"ca": [ {"nickname": "A0", "cn": "A1", "subca": [ {"nickname": "B0", "cn": "B1",
            "cert": [ {"nickname": "C0"}, {"nickname": "B0"}]}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

    def test_default_values(self):
        """Tests parsing a conf file with default values."""
        data = """ { "ca": [ {"nickname": "example", "cn": "Example CA"} ] } """
        cnf = conf.parse(data)
        self.assertEqual("error", cnf["logging"]["level"])
        self.assertEqual("syslog", cnf["logging"]["handler"])

    def test_logging(self):
        """Tests parsing a conf file with logging settings."""
        # try the different logging levels and make sure the default handler is set
        levels = ["debug", "info", "warning", "error"]
        for level in levels:
            d = """ { "ca": [ {"nickname": "a", "cn": "b"} ], "logging": { "level": "%s" } } """ % level
            cnf = conf.parse(d)
            self.assertEqual(level, cnf["logging"]["level"])
            self.assertEqual("syslog", cnf["logging"]["handler"])

        # try an invalid level
        d = """ { "ca": [ {"nickname": "a", "cn": "b"} ], "logging": { "level": "foo" } } """
        with self.assertRaises(ValueError):
            conf.parse(d)

        # try the different handlers and make sure the default level is set
        d = """ { "ca": [ {"nickname": "a", "cn": "b"} ], "logging": { "handler": "syslog" } } """
        cnf = conf.parse(d)
        self.assertEqual("syslog", cnf["logging"]["handler"])
        self.assertEqual("error", cnf["logging"]["level"])

        d = """ { "ca": [ {"nickname": "a", "cn": "b"} ], "logging": { "handler": "file", "filename": "a.txt" } } """
        cnf = conf.parse(d)
        self.assertEqual("file", cnf["logging"]["handler"])
        self.assertEqual("a.txt", cnf["logging"]["filename"])
        self.assertEqual("error", cnf["logging"]["level"])

        # make sure the filename is not parsed if the handler is not 'file'
        d = """ { "ca": [ {"nickname": "a", "cn": "b"} ], "logging": { "handler": "syslog" } } """
        cnf = conf.parse(d)
        self.assertEqual("syslog", cnf["logging"]["handler"])
        self.assertNotIn("filename", cnf["logging"])

        # set all the options with 'syslog'
        d = """ { "ca": [ {"nickname": "a", "cn": "b"} ], "logging": { "handler": "syslog", "level": "info" } } """
        cnf = conf.parse(d)
        self.assertEqual("syslog", cnf["logging"]["handler"])
        self.assertEqual("info", cnf["logging"]["level"])

        # set all the options with 'file'
        d = """ { "ca": [ {"nickname": "a", "cn": "b"} ],
            "logging": { "handler": "file", "filename": "a.txt", "level": "debug" } } """
        cnf = conf.parse(d)
        self.assertEqual("file", cnf["logging"]["handler"])
        self.assertEqual("a.txt", cnf["logging"]["filename"])
        self.assertEqual("debug", cnf["logging"]["level"])

    def test_validity(self):
        """Test parsing a conf file with validity setting."""
        # test default validity of ca
        data = """{"ca": [{"nickname": "A", "cn": "B"}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual(365 * 5, cnf["ca"][0]["validity"])

        # simple ca example
        data = """{"ca": [{"nickname": "A", "cn": "B", "validity": 30}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual(30, cnf["ca"][0]["validity"])

        # error validity ca
        data = """{"ca": [{"nickname": "A", "cn": "B", "validity": 0}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "validity": -1}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # test default validity of subca
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D"}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual(365 * 5, cnf["ca"][0]["subca"][0]["validity"])

        # simple subca example
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D", "validity": 13}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual(13, cnf["ca"][0]["subca"][0]["validity"])

        # error validity subca
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D", "validity": 0}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D", "validity": -1}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # test default validity of cert
        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C"}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual(365, cnf["ca"][0]["cert"][0]["validity"])

        # simple cert example
        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C", "validity": 1345}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual(1345, cnf["ca"][0]["cert"][0]["validity"])

        # error validity cert
        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C", "validity": 0}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C", "validity": -1}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

    def test_crl_validity(self):
        """Test parsing a conf file with crl validity setting."""
        # test default crl validity of ca
        data = """{"ca": [{"nickname": "A", "cn": "B"}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual(365, cnf["ca"][0]["crl_validity"])

        # simple ca example
        data = """{"ca": [{"nickname": "A", "cn": "B", "crl_validity": 30}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual(30, cnf["ca"][0]["crl_validity"])

        # error validity ca
        data = """{"ca": [{"nickname": "A", "cn": "B", "crl_validity": 0}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "crl_validity": -1}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # test default crl validity of subca
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D"}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual(365, cnf["ca"][0]["subca"][0]["crl_validity"])

        # simple subca example
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "crl_validity": 13}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual(13, cnf["ca"][0]["subca"][0]["crl_validity"])

        # error crl validity subca
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "crl_validity": 0}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D",
            "crl_validity": -1}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

    def test_keysize(self):
        """Test parsing a conf file with keysize setting."""
        # test default keysize of ca
        data = """{"ca": [{"nickname": "A", "cn": "B"}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual(4096, cnf["ca"][0]["keysize"])

        # simple ca example
        data = """{"ca": [{"nickname": "A", "cn": "B", "keysize": 2048}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual(2048, cnf["ca"][0]["keysize"])

        data = """{"ca": [{"nickname": "A", "cn": "B", "keysize": 4096}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual(4096, cnf["ca"][0]["keysize"])

        # error keysize ca
        data = """{"ca": [{"nickname": "A", "cn": "B", "keysize": 2112}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "keysize": -1}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # test default keysize of subca
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D"}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual(4096, cnf["ca"][0]["subca"][0]["keysize"])

        # simple subca example
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D", "keysize": 2048}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual(2048, cnf["ca"][0]["subca"][0]["keysize"])

        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D", "keysize": 4096}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["subca"][0]["nickname"])
        self.assertEqual("D", cnf["ca"][0]["subca"][0]["cn"])
        self.assertEqual(4096, cnf["ca"][0]["subca"][0]["keysize"])

        # error keysize subca
        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D", "keysize": 4097}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "subca": [{"nickname": "C", "cn": "D", "keysize": -1}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        # test default keysize of cert
        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C"}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual(4096, cnf["ca"][0]["cert"][0]["keysize"])

        # simple cert example
        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C", "keysize": 2048}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual(2048, cnf["ca"][0]["cert"][0]["keysize"])

        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C", "keysize": 4096}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual("A", cnf["ca"][0]["nickname"])
        self.assertEqual("B", cnf["ca"][0]["cn"])
        self.assertEqual("C", cnf["ca"][0]["cert"][0]["nickname"])
        self.assertEqual(4096, cnf["ca"][0]["cert"][0]["keysize"])

        # error keysize cert
        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C", "keysize": 1200}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

        data = """{"ca": [{"nickname": "A", "cn": "B", "cert": [{"nickname": "C", "keysize": -1}]}]}"""
        with self.assertRaises(ValueError):
            conf.parse(data)

    def test_find_issuer_cert(self):
        """Tests finding an cert and issuer in a conf."""
        # no entities
        data = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(data)
        self.assertEqual(conf.find_issuer_cert(cnf, "b"), (None, None))

        # cert under a single ca
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "cn": "B"}]}]}"""
        cnf = conf.parse(data)
        (issuer, cert) = conf.find_issuer_cert(cnf, "b")
        self.assertEqual("a", issuer["nickname"])
        self.assertEqual("b", cert["nickname"])

        # cert under a ca with multiple ca
        data = """{"ca": [{"nickname": "a", "cn": "A"}, {"nickname": "b", "cn": "B", "cert":
            [{"nickname": "c", "cn": "C"}]}]}"""
        cnf = conf.parse(data)
        (issuer, cert) = conf.find_issuer_cert(cnf, "c")
        self.assertEqual("b", issuer["nickname"])
        self.assertEqual("c", cert["nickname"])

        # cert under a single subca
        data = """{"ca": [{"nickname": "a", "cn": "A", "subca": [{"nickname": "b", "cn": "B", "cert": [
            {"nickname": "c", "cn": "C"}]}]}]}"""
        cnf = conf.parse(data)
        (issuer, cert) = conf.find_issuer_cert(cnf, "c")
        self.assertEqual("b", issuer["nickname"])
        self.assertEqual("c", cert["nickname"])

        # multiple entities but not found
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "cn": "B"}, {"nickname": "c",
            "cn": "C"}, {"nickname": "d", "cn": "D"}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual(conf.find_issuer_cert(cnf, "e"), (None, None))

        # try to find a cert but use the ca nickname
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "cn": "B"}, {"nickname": "c",
            "cn": "C"}, {"nickname": "d", "cn": "D"}]}]}"""
        cnf = conf.parse(data)
        self.assertEqual(conf.find_issuer_cert(cnf, "a"), (None, None))

        # cert under multiple subca of multiple ca
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "cn": "B"}]}, {"nickname": "c",
            "cn": "C", "subca": [{"nickname": "d", "cn": "D"}, {"nickname": "e", "cn": "E", "cert": [
            {"nickname": "f", "cn": "F"}, {"nickname": "g", "cn": "G"}]}]}]}"""
        cnf = conf.parse(data)
        (issuer, cert) = conf.find_issuer_cert(cnf, "g")
        self.assertEqual("e", issuer["nickname"])
        self.assertEqual("g", cert["nickname"])


    def test_find_profile(self):
        """Tests finding an profile in a conf."""
        # single ca
        data = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(data)
        profile = conf.find_profile(cnf, "a")
        self.assertIsNotNone(profile)
        self.assertEqual("A", profile["cn"])
        profile = conf.find_profile(cnf, "z")
        self.assertIsNone(profile)

        # cert under a single ca
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "ou": "B"}]}]}"""
        cnf = conf.parse(data)
        profile = conf.find_profile(cnf, "b")
        self.assertIsNotNone(profile)
        self.assertEqual("B", profile["ou"])
        profile = conf.find_profile(cnf, "a")
        self.assertIsNotNone(profile)
        self.assertEqual("A", profile["cn"])
        profile = conf.find_profile(cnf, "z")
        self.assertIsNone(profile)

        # cert under a ca with multiple ca
        data = """{"ca": [{"nickname": "a", "cn": "A"}, {"nickname": "b", "cn": "B", "cert":
            [{"nickname": "c", "ou": "C"}]}]}"""
        cnf = conf.parse(data)
        profile = conf.find_profile(cnf, "c")
        self.assertIsNotNone(profile)
        self.assertEqual("C", profile["ou"])
        profile = conf.find_profile(cnf, "b")
        self.assertIsNotNone(profile)
        self.assertEqual("B", profile["cn"])
        profile = conf.find_profile(cnf, "a")
        self.assertIsNotNone(profile)
        self.assertEqual("A", profile["cn"])
        profile = conf.find_profile(cnf, "z")
        self.assertIsNone(profile)

        # cert under a single subca
        data = """{"ca": [{"nickname": "a", "cn": "A", "subca": [{"nickname": "b", "cn": "B", "cert": [
            {"nickname": "c", "ou": "C"}]}]}]}"""
        cnf = conf.parse(data)
        profile = conf.find_profile(cnf, "c")
        self.assertIsNotNone(profile)
        self.assertEqual("C", profile["ou"])
        profile = conf.find_profile(cnf, "b")
        self.assertIsNotNone(profile)
        self.assertEqual("B", profile["cn"])
        profile = conf.find_profile(cnf, "a")
        self.assertIsNotNone(profile)
        self.assertEqual("A", profile["cn"])
        profile = conf.find_profile(cnf, "z")
        self.assertIsNone(profile)

        # cert under multiple subca of multiple ca
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "ou": "B"}]}, {"nickname": "c",
            "cn": "C", "subca": [{"nickname": "d", "cn": "D"}, {"nickname": "e", "cn": "E", "cert": [
            {"nickname": "f", "ou": "F"}, {"nickname": "g", "ou": "G"}]}]}]}"""
        cnf = conf.parse(data)
        profile = conf.find_profile(cnf, "g")
        self.assertEqual("G", profile["ou"])
        self.assertIsNotNone(profile)
        profile = conf.find_profile(cnf, "f")
        self.assertIsNotNone(profile)
        self.assertEqual("F", profile["ou"])
        profile = conf.find_profile(cnf, "e")
        self.assertIsNotNone(profile)
        self.assertEqual("E", profile["cn"])
        profile = conf.find_profile(cnf, "d")
        self.assertIsNotNone(profile)
        self.assertEqual("D", profile["cn"])
        profile = conf.find_profile(cnf, "c")
        self.assertIsNotNone(profile)
        self.assertEqual("C", profile["cn"])
        profile = conf.find_profile(cnf, "b")
        self.assertIsNotNone(profile)
        self.assertEqual("B", profile["ou"])
        profile = conf.find_profile(cnf, "a")
        self.assertIsNotNone(profile)
        self.assertEqual("A", profile["cn"])
        profile = conf.find_profile(cnf, "z")
        self.assertIsNone(profile)

    def test_find_issuer(self):
        """Tests finding an issuer in a conf."""
        # single ca
        data = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(data)
        issuer = conf.find_issuer(cnf, "a")
        self.assertIsNotNone(issuer)
        self.assertEqual("A", issuer["cn"])
        issuer = conf.find_issuer(cnf, "z")
        self.assertIsNone(issuer)

        # more complex example
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "ou": "B"}]}, {"nickname": "c",
            "cn": "C", "subca": [{"nickname": "d", "cn": "D"}, {"nickname": "e", "cn": "E", "cert": [
            {"nickname": "f", "ou": "F"}, {"nickname": "g", "ou": "G"}]}]}]}"""
        cnf = conf.parse(data)
        issuer = conf.find_issuer(cnf, "g")
        self.assertIsNone(issuer)
        issuer = conf.find_issuer(cnf, "f")
        self.assertIsNone(issuer)
        issuer = conf.find_issuer(cnf, "e")
        self.assertIsNotNone(issuer)
        self.assertEqual("E", issuer["cn"])
        issuer = conf.find_issuer(cnf, "d")
        self.assertIsNotNone(issuer)
        self.assertEqual("D", issuer["cn"])
        issuer = conf.find_issuer(cnf, "c")
        self.assertIsNotNone(issuer)
        self.assertEqual("C", issuer["cn"])
        issuer = conf.find_issuer(cnf, "b")
        self.assertIsNone(issuer)
        issuer = conf.find_issuer(cnf, "a")
        self.assertIsNotNone(issuer)
        self.assertEqual("A", issuer["cn"])
        issuer = conf.find_issuer(cnf, "z")
        self.assertIsNone(issuer)

    def test_find_issuers(self):
        """Tests getting all the issuers in the conf file."""
        # single ca
        data = """{"ca": [{"nickname": "a", "cn": "A"}]}"""
        cnf = conf.parse(data)
        results = conf.find_issuers(cnf)
        self.assertEqual(1, len(results))
        self.assertEqual("a", results[0]["nickname"])

        # a complex conf
        data = """{"ca": [{"nickname": "a", "cn": "A", "cert": [{"nickname": "b", "ou": "B"}]}, {"nickname": "c",
            "cn": "C", "subca": [{"nickname": "d", "cn": "D"}, {"nickname": "e", "cn": "E", "cert": [
            {"nickname": "f", "ou": "F"}, {"nickname": "g", "ou": "G"}]}]}]}"""
        cnf = conf.parse(data)
        results = conf.find_issuers(cnf)
        self.assertEqual(4, len(results))

        # remove all the nicknames and check the expected set is empty
        expected = {"a", "c", "d", "e"}
        for issuer in results:
            expected.remove(issuer["nickname"])
        self.assertEqual(0, len(expected))
