__version__ = '0.6.3'  # setup.py needs this to be the first line in this file

from .args import HelpfulArgumentParser
from .io.fasta import (
	SequenceReader, FastaReader, FastqReader, FastaWriter, FastqWriter,
	IndexedFasta, guess_quality_base )
from .io.gtf import GtfReader
from cutadapt.xopen import xopen
from .cigar import Cigar
