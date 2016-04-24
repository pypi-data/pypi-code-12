import subprocess
from collections import Counter
from io import StringIO

from .io.fasta import FastaReader
from .utils import available_cpu_count

from sqt._helpers import globalalign, hamming_distance


class GlobalAlignment:
	"""A global alignment between two strings"""

	def __init__(self, s, t, semiglobal=False):
		if type(s) is str:
			s = s.encode('ascii')
		if type(t) is str:
			t = t.encode('ascii')
		flags = 15 if semiglobal else 0  # TODO this constant shouldn't be here
		# globalalign uses scores. Set match to 0 to get the same result as with
		# edit distance unless we compute semiglobal alignments, where edit
		# distance does not work.
		match = 1 if semiglobal else 0
		(row1, row2, start1, stop1, start2, stop2, errors) = globalalign(s, t, flags=flags, match=match)
		assert semiglobal or start1 == start2 == 0
		assert semiglobal or stop1 == len(s)
		assert semiglobal or stop2 == len(t)
		assert len(row1) == len(row2)
		self.row1 = row1.decode('ascii')
		self.row2 = row2.decode('ascii')
		self.start1 = start1
		self.stop1 = stop1
		self.start2 = start2
		self.stop2 = stop2
		self.errors = errors
		# Overlap start and stop in alignment coordinates.
		# row1[overlap_start:overlap_stop] is the overlapping alignment.
		self.overlap_start = max(start1, start2)
		self.overlap_stop = len(row1) - max(len(s) - stop1, len(t) - stop2)

	def _replace_gaps(self, row, gap_char):
		start = self.overlap_start
		stop = self.overlap_stop
		front = row[:start].replace('\0', ' ')
		middle = row[start:stop].replace('\0', gap_char)
		end = row[stop:].replace('\0', ' ')
		return front + middle + end

	def print(self, width=100, gap_char='-'):
		"""multi-line output and parameters, therefore not called __str__"""
		row1 = self._replace_gaps(self.row1, gap_char)
		row2 = self._replace_gaps(self.row2, gap_char)
		for i in range(0, len(row1), width):
			top = row1[i:i+width]
			bottom = row2[i:i+width]
			m = []
			for c, d in zip(top, bottom):
				if c == d:
					m.append('|')
				elif c == ' ' or d == ' ':
					m.append(' ')
				else:
					m.append('X')
			middle = ''.join(m)
			if i > 0:
				print()
			print(top)
			print(middle)
			print(bottom)

	def __str__(self):
		return 'GA(row1={}, row2={}, errors={})'.format(
			self.row1, self.row2, self.errors)


def edit_distance(s, t, maxdiff=-1):
	"""
	Return the edit distance between the strings s and t.
	The edit distance is the sum of the numbers of insertions, deletions,
	and mismatches that is minimally necessary to transform one string
	into the other.

	If maxdiff is not -1, then a banded alignment is performed. In that case,
	the true edit distance is returned if and only if it is maxdiff or less.
	Otherwise, a value is returned that is guaranteed to be greater than
	maxdiff, but which is not necessarily the true edit distance.
	"""
	m = len(s) # index: i
	n = len(t) # index: j

	e = maxdiff
	if e != -1 and abs(m - n) > e:
		return abs(m - n)

	# dynamic programming "table" (just a single column)
	# note that using an array('h', ...) here is not faster
	costs = list(range(m+1))

	# calculate alignment (using unit costs)
	for j in range(1, n+1):
		start = 1
		stop = m + 1
		if e != -1: # banded
			stop = min(stop, j + e + 1)
			if j <= e:
				prev = costs[0]
				costs[0] += 1
				start = 1
			else:
				start = j - e
				prev = costs[start-1]
		else:
			prev = costs[0]
			costs[0] += 1
		for i in range(start, stop):
			c = min(
				prev + int(s[i-1] != t[j-1]),
				costs[i] + 1,
				costs[i-1] + 1)
			prev = costs[i]
			costs[i] = c

	return costs[-1]


try:
	from sqt._helpers import edit_distance
except:
	pass


def multialign(sequences, program='mafft', threads=available_cpu_count()):
	"""
	Wrapper for multiple sequence alignment tools. Currently supported are
	* ClustalO (http://www.clustal.org/omega/),
	* MAFFT (http://mafft.cbrc.jp/alignment/software/)
	* MUSCLE (http://www.drive5.com/muscle/)

	A package using the libclustalo library directly also exists:
	https://github.com/benchling/clustalo-python/blob/master/clustalo.c
	It is not for Python 3.

	sequences -- a dictionary mapping names to sequences.
		Use an OrderedDict if order matters.

	program -- must be 'clustalo', 'mafft', 'muscle', 'muscle-medium',
		'muscle-fast'. The latter calls MUSCLE with parameters that make it run
		faster (but less accurate). 'muscle-medium' is in between muscle and
		muscle-fast.

	threads -- number of threads to use for those programs that support it.
		By default, set to the number of processors.
	"""
	if program == 'mafft':
		args = ['mafft', '--quiet', '--thread', str(threads), '-']
	elif program == 'clustalo':
		args = ['clustalo', '--threads='+str(threads), '--infile=-']
	elif program == 'muscle':
		args = ['muscle', '-quiet', '-in', '-', '-out', '-']
	elif program == 'muscle-fast':
		args = ['muscle', '-quiet', '-maxiters', '1', '-diags', '-in', '-', '-out', '-']
	elif program == 'muscle-medium':
		args = ['muscle', '-quiet', '-maxiters', '2', '-diags', '-in', '-', '-out', '-']
	else:
		raise ValueError('program {!r} not supported'.format(program))

	fasta_data = ''.join('>{}\n{}\n'.format(name, seq) for name, seq in sequences.items())
	result = subprocess.check_output(args, input=fasta_data, universal_newlines=True)
	aligned = list(FastaReader(StringIO(result)))

	return { record.name: record.sequence.upper() for record in aligned }


def consensus(aligned, threshold=0.7, ambiguous='N', keep_gaps=False):
	"""
	Compute a consensus from multialign() output.

	Idea taken from BioPython’s SummaryInfo.dumb_consensus function.

	aligned -- a dict mapping names to sequences or a list of sequences
	keep_gaps -- whether the returned sequence contains gaps (-)
	"""
	result = []
	n = len(aligned)
	if hasattr(aligned, 'values'):
		sequences = aligned.values()
	else:
		sequences = aligned
	ambiguous = 'N'
	for chars in zip(*sequences):
		char, freq = Counter(chars).most_common(1)[0]
		if freq / n >= threshold:
			if keep_gaps or char != '-':
				result.append(char)
		else:
			result.append(ambiguous)
	return ''.join(result)
