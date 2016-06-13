from vcf import Reader


class VariantAssertions:

    def assertVcfHasVariantAt(self, vcf, chrom, pos):
        v = Reader(filename=vcf)
        variants = v.fetch(chrom=chrom, start=pos - 1, end=pos)
        variant_found = False
        for variant in variants:
            if variant.CHROM == str(chrom) and variant.POS == pos:
                variant_found = True

        if not variant_found:
            raise AssertionError("Variant at {}:{} not present in {}".format(
                chrom, pos, vcf))

    def assertVcfHasVariantWithChromPosRefAlt(self, vcf, chrom, pos, ref, alt):
        v = Reader(filename=vcf)
        variants = v.fetch(chrom=chrom, start=pos - 1, end=pos)
        variant_found = False
        for variant in variants:
            if variant.CHROM == str(chrom) and \
                    variant.POS == pos and \
                    variant.REF == ref and \
                    alt in variant.ALT:
                variant_found = True

        if not variant_found:
            raise AssertionError(
                "Variant at {}:{} {}/{} not present in {}".format(chrom, pos,
                                                                  ref, alt,
                                                                  vcf))

    def assertVcfHasVariantWithChromPosId(self, vcf, chrom, pos, variant_id):
        v = Reader(filename=vcf)
        variants = v.fetch(chrom=chrom, start=pos - 1, end=pos)
        variant_found = False
        for variant in variants:
            if variant.CHROM == str(chrom) \
                    and variant.POS == pos \
                    and variant.ID == str(variant_id):
                variant_found = True

        if not variant_found:
            raise AssertionError("Variant at {}:{} with id {} not present in {}".format(
                chrom, pos, variant_id, vcf))

    def assertVcfHasSample(self, vcf, sample):
        v = Reader(filename=vcf)
        if sample not in v.samples:
            raise AssertionError("Sample {} not present in {}".format(
                sample, vcf))

    def assertVcfHasVariantWithCall(self, vcf, chrom, pos, sample, call):
        """
        Assert that a call is made for a given sample in a given position. `call` is a dict corresponding to elements
        in the vcf sample field. Example:

        self.assertVcfHasVariantWithCall(my_vcf, 1, 3184885, 'B',
                                         call={'GT': '1/2', 'DP': 10})
        """
        self.assertVcfHasSample(vcf, sample)

        v = Reader(filename=vcf)
        variants = v.fetch(chrom=chrom, start=pos - 1, end=pos)
        variant_found = False
        for variant in variants:
            if variant.CHROM == str(chrom) and variant.POS == pos:
                for cc in variant.samples:
                    if cc.sample == sample:
                        # thank you http://stackoverflow.com/a/4527978/179444
                        shared_items = set(cc.data.__dict__.items()) & set(call.items())
                        if shared_items == set(call.items()):
                            variant_found = True

        if not variant_found:
            raise AssertionError("Call {} not present for sample {} at {}:{} in {}".format(
                call, sample, chrom, pos, vcf))
