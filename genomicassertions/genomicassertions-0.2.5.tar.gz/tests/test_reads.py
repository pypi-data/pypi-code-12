import unittest
from genomicassertions.readassertions import ReadAssertions


class TestReads(unittest.TestCase, ReadAssertions):
    bam = "tests/3_178936091.bam"

    def test_has_coverage_as_pos(self):
        self.assertBamHasCoverageAt(self.bam, 324, 3, 178936091)

    def test_has_0_coverage_at_pos(self):
        self.assertBamHasCoverageAt(self.bam, 0, 3, 1337)

    def test_nonzero_coverage_at_pos(self):
        with self.assertRaises(AssertionError):
            self.assertBamHasCoverageAt(self.bam, 42, 3, 1337)

    def test_raises_if_incorrect_coverage(self):
        with self.assertRaises(AssertionError):
            self.assertBamHasCoverageAt(self.bam, 323, 3, 178936091)

    def test_bam_has_header_element(self):
        self.assertBamHasHeaderElement(self.bam, "HD")

    def test_raises_if_header_element_not_in_bam(self):
        with self.assertRaises(AssertionError):
            self.assertBamHasHeaderElement(self.bam, "FOO")

    def test_header_element_equals(self):
        self.assertBamHeaderElementEquals(self.bam, 'HD', {'SO': 'coordinate',
                                                           'VN': '1.3'})

    def assert_raises_if_test_header_element_not_equals(self):
        # one wrong key in element
        with self.assertRaises(AssertionError):
            self.assertBamHeaderElementEquals(self.bam, 'HD',
                                              {'SO': 'coordinate',
                                               'VN': '1.4'})

        # no element with name
        with self.assertRaises(AssertionError):
            self.assertBamHeaderElementEquals(self.bam, 'FOO',
                                              {'SO': 'coordinate',
                                               'VN': '1.4'})
