import pysam


class ReadAssertions:

    def assertBamHasCoverageAt(self, bam, coverage, chrom, pos):
        samfile = pysam.AlignmentFile(bam, "rb")
        iter = samfile.pileup('3', pos - 1, pos, truncate=True)
        try:
            pile = iter.next()
            if pile.nsegments != coverage:
                raise AssertionError(
                    "Coverage at {}:{} was not {} in {} (got {})".format(
                        chrom, pos, coverage, bam, pile.nsegments))
        except StopIteration:
            if coverage != 0:
                raise AssertionError(
                    "Coverage at {}:{} was zero in {}".format(
                        chrom, pos, bam))

    def assertBamHasHeaderElement(self, bam, header_element):
        samfile = pysam.AlignmentFile(bam, "rb")
        if header_element not in samfile.header:
            raise AssertionError(
                "Header element {} not in header of {}".format(header_element,
                                                               bam))

    def assertBamHeaderElementEquals(self, bam, header_element_name,
                                     header_element_value):
        samfile = pysam.AlignmentFile(bam, "rb")
        self.assertBamHasHeaderElement(bam, header_element_name)

        if samfile.header[header_element_name] != header_element_value:
            raise AssertionError(
                "Header element for key {} is incorrect. Check {}, got {}.".format(
                    header_element_name,
                    header_element_value,
                    samfile.header[header_element_name]))
