import unittest
import bloomzip
import os

_IN_SET = ["lorem", "felis", "urna"]
_OUT_OF_SET = ["english", "words"]


class BloomZipTest(unittest.TestCase):
    def test_bloomzip(self):
        with open("test/uncompressed.txt", 'r') as f:
            words = " ".join(f.readlines()).lower().split()

        assert(set(words).intersection(_IN_SET) == set(_IN_SET))
        assert (set(words).intersection(_OUT_OF_SET) == set())

        with bloomzip.BloomZip(
            "test/compressed.blzip") as bl, open(
                "test/uncompressed.txt", 'r') as uc:
            a = uc.read()
            bl.write(a)

        with bloomzip.BloomZip("test/compressed.blzip") as bl:
            for i in _IN_SET:
                self.assertTrue(bl.contains(i))
            for i in _OUT_OF_SET:
                self.assertFalse((bl.contains(i)))

    def tearDown(self):
        os.remove("test/compressed.blzip")
