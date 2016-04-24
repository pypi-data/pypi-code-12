"""
Minimalistic GTF parsing.
"""
from collections import namedtuple
from ..io.xopen import xopen

GtfRecord = namedtuple('GtfRecord',
	['chrom', 'source', 'feature', 'start', 'stop', 'score', 'strand', 'frame',
		'attributes'
	])


# this parser is very simplistic. It is only made to be able to parse ENSEMBL files such as these:
# ftp://ftp.ensembl.org/pub/release-66/gtf/homo_sapiens/Homo_sapiens.GRCh37.66.gtf.gz
#
# First line in that file:
# GL000213.1 protein_coding exon 138767 139339 . - . gene_id "ENSG00000237375"; transcript_id "ENST00000327822";
#    exon_number "1"; gene_name "BX072566.1"; gene_biotype "protein_coding"; transcript_name "BX072566.1-201";


def _none_or_type(s, type):
	return None if s == '.' else type(s)


def GtfReader(path):
	"""Iterate over the GTF file named by given path. Yield GtfRecord objects."""
	with xopen(path) as f:
		for line in f:
			if line.startswith('#'):
				continue
			line = line.rstrip('\n\r')
			fields = line.split('\t')
			chrom = fields[0]
			source = fields[1]
			feature = fields[2]
			start = int(fields[3]) - 1
			stop = int(fields[4])
			score = _none_or_type(fields[5], float)
			strand = fields[6]
			frame = _none_or_type(fields[7], int)
			assert strand in '+-'
			assert frame in (None, 0, 1, 2)

			atts = fields[8].strip(' ').split(';')
			attributes = dict()
			for att in atts:
				att = att.strip(' ')
				if not att:
					continue
				name, value = att.split(' ', maxsplit=1)
				value = value.strip('"')
				attributes[name] = value
			yield GtfRecord(
				chrom=chrom,
				source=source,
				feature=feature,
				start=start,
				stop=stop,
				score=score,
				strand=strand,
				frame=frame,
				attributes=attributes
			)


def main():
	import sys
	for record in parse_gtf(sys.argv[1]):
		print(record)

if __name__ == '__main__':
	main()
