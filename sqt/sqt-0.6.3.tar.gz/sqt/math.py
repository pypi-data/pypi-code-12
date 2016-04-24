def frequency_median(frequencies):
	"""
	Given a dictionary of frequencies, return the median.
	If the total no. of values is odd, the left of both
	middle values is returned.
	"""
	m = 0  # partial sum
	middle = (1 + sum(frequencies.values())) // 2
	for length in sorted(frequencies):
		m += frequencies[length]
		if m >= middle:
			return length
	# never reached
	assert False


def frequency_n50(lengths, genome_size=None):
	"""
	Return N50 or NG50 value given a Counter of lengths.

	If the genome_size is not given, it is set to the total length. The resulting
	value is the N50. If it is given, the resulting value is the NG50.

	If genome_size is greater than two times the number of sequences, None is returned.
	"""
	if genome_size is None:
		genome_size = sum(length * count for length, count in lengths.items())
	running_total = 0
	for length in sorted(lengths, reverse=True):
		running_total += length * lengths[length]
		if running_total >= genome_size * 0.5:
			return length
	return None


def n50(lengths, genome_size=None):
	"""
	Return N50 or NG50 value given a list of lengths.

	If the genome_size is not given, it is set to sum(lengths). The resulting
	value is the N50. If it is given, the resulting value is the NG50.

	If genome_size is greater than 2 * sum(lengths), None is returned.
	"""
	if genome_size is None:
		genome_size = sum(lengths)
	lengths = sorted(lengths, reverse=True)
	running_total = 0
	for length in lengths:
		running_total += length
		if running_total >= genome_size * 0.5:
			return length
	return None
