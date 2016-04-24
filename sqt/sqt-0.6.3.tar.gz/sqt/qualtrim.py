"""
Quality trimming and filtering.
"""
from cutadapt.qualtrim import quality_trim_index as _qtrimindex

def quality_trim_index(qualities, cutoff, base=33):
	return _qtrimindex(qualities, 0, cutoff, base=base)[1]


def expected_errors(qualities, base=33):
	"""
	Return expected number of errors.

	qualities -- ASCII-encoded qualities (chr(qual + base)).
	"""
	return sum(10 ** (-(ord(q) - base) / 10) for q in qualities)


try:
	from ._helpers import expected_errors
except ImportError:
	pass
