"""
Model an interval on a reference.
"""
class Region:
	def __init__(self, specification, start=None, stop=None, reverse_complement=False):
		"""
		specification -- description of the region as a string, such as
		"chr14:22-111"

		If start is given, the specification is considered to be a reference and
		the parameters start, stop, reverse_complement are used directly.
		"""
		if start is None:
			self.reference, self.start, self.stop, self.is_reverse_complement = self._parse_region(specification)
		else:
			self.reference = specification
			self.start = start
			self.stop = stop
			self.is_reverse_complement = reverse_complement

	@staticmethod
	def _parse_region(s):
		"""
		Parse a string like "name:begin-end" or "name:begin..end".
		The returned tuple is (name, start, stop, revcomp).
		start is begin-1, stop is equal to end.
		That is, this function converts from 1-based intervals to pythonic
		open intervals!

		The string may be prefixed with "rc:", in which case revcomp is set to True.

		If 'end' is an empty string (as in "chrx:1-"), then stop is set to None.
		If no range is given, as in "chrx:27", then stop is set to start+1.
		If only 'name' is given (or "rc:name"), start is set to 0 and stop to None.

		Commas within the numbers (thousands separators) are ignored.
		"""
		revcomp = False
		if s.startswith('rc:'):
			revcomp = True
			s = s[3:]
		fields = s.rsplit(':', 1)
		if len(fields) == 1:
			region = (fields[0], 0, None, revcomp)
		else:
			if '..' in fields[1]:
				sep = '..'
			else:
				sep = '-'
			coords = fields[1].split(sep, maxsplit=1)
			start = int(coords[0].replace(',', ''))
			if len(coords) == 1:
				stop = start
			else:
				stop = int(coords[1].replace(',', '')) if coords[1] != '' else None
			assert 0 < start and (stop is None or start <= stop)
			region = (fields[0], start-1, stop, revcomp)
		return region

	def __str__(self):
		"""

		"""
		prefix = 'rc:' if self.is_reverse_complement else ''
		if self.start == 0 and self.stop is None:
			return prefix + self.reference
		if self.start + 1 == self.stop:
			return "{}{}:{}".format(prefix, self.reference, self.start+1)
		stop = '' if self.stop is None else self.stop
		return "{}{}:{}-{}".format(prefix, self.reference, self.start+1, stop)

	def __repr__(self):
		return "Region({!r})".format(str(self))

	def __eq__(self, other):
		return (self.reference == other.reference and self.start == other.start
		  and self.stop == other.stop
		  and self.is_reverse_complement == other.is_reverse_complement)
