import unittest
from genomicassertions.variantassertions import VariantAssertions


class TestVariants(unittest.TestCase, VariantAssertions):
    vcf = "tests/variants.vcf.gz"
    vcf_with_genotypes = "tests/variants-with-genotypes.vcf.gz"

    def test_variant_at(self):
        self.assertVcfHasVariantAt(self.vcf, 3, 178936091)

    def test_variant_with_chrom_pos_ref_alt(self):
        self.assertVcfHasVariantWithChromPosRefAlt(self.vcf_with_genotypes, 1, 3062915, 'G', 'C')
        self.assertVcfHasVariantWithChromPosRefAlt(self.vcf_with_genotypes, 1, 3062915, 'G', 'T')

    def test_variant_with_id(self):
        self.assertVcfHasVariantWithChromPosId(self.vcf_with_genotypes, 1, 3062915, 'id3D')

    def test_vcf_has_sample(self):
        self.assertVcfHasSample(self.vcf_with_genotypes, 'B')

    def test_vcf_has_variant_with_call(self):
        self.assertVcfHasVariantWithCall(self.vcf_with_genotypes, 1, 3184885, 'B',
                                         {'GT': '1/2', 'DP': 10})

    def test_raises_if_variant_missing(self):
        with self.assertRaises(AssertionError):
            self.assertVcfHasVariantAt(self.vcf, 3, 178936092)

        with self.assertRaises(AssertionError):
            self.assertVcfHasVariantWithChromPosRefAlt(self.vcf_with_genotypes, 1, 3062915, 'G', 'A')

        with self.assertRaises(AssertionError):
            self.assertVcfHasVariantWithChromPosId(self.vcf_with_genotypes, 1, 3062915, 'foo')

    def test_raises_if_sample_missing(self):
        with self.assertRaises(AssertionError):
            self.assertVcfHasSample(self.vcf_with_genotypes, 'foo')

        with self.assertRaises(AssertionError):
            # raise if sample is missing
            self.assertVcfHasVariantWithCall(self.vcf_with_genotypes, 1, 3184885, 'FOO',
                                             {'GT': '1/2', 'DP': 10})

    def test_raises_if_call_not_present(self):
        with self.assertRaises(AssertionError):
            self.assertVcfHasVariantWithCall(self.vcf_with_genotypes, 1, 3184885, 'B',
                                             {'GT': '1/2', 'DP': 9})

        with self.assertRaises(AssertionError):
            self.assertVcfHasVariantWithCall(self.vcf_with_genotypes, 1, 3184885, 'B',
                                             {'GT': '1/2', 'FOO': 'bar'})
