# | Copyright 2014-2016 Karlsruhe Institute of Technology
# |
# | Licensed under the Apache License, Version 2.0 (the "License");
# | you may not use this file except in compliance with the License.
# | You may obtain a copy of the License at
# |
# |     http://www.apache.org/licenses/LICENSE-2.0
# |
# | Unless required by applicable law or agreed to in writing, software
# | distributed under the License is distributed on an "AS IS" BASIS,
# | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# | See the License for the specific language governing permissions and
# | limitations under the License.

from grid_control.utils.data_structures import makeEnum
from grid_control.utils.gc_itertools import ichain
from grid_control.utils.parsing import strDict
from hpfwk import APIError, NestedException
from python_compat import ifilter, imap, lfilter, lmap, set, sorted

class ConfigError(NestedException):
	pass

# Placeholder to specify a non-existing default
noDefault = makeEnum(['noDefault'])

# return canonized section or option string
def standardConfigForm(value):
	if value is not None:
		if not isinstance(value, list):
			value = [value]
		return lmap(lambda x: str(x).strip().lower(), value)


def appendOption(option, suffix):
	if isinstance(option, (list, tuple)):
		return lmap(lambda x: appendOption(x, suffix), option)
	return option.rstrip() + ' ' + suffix


# Holder of config information
class ConfigEntry(object):
	def __init__(self, section, option, value, opttype, source, order = None, accessed = False, used = False):
		(self.section, self.option, self.source, self.order) = (section.lower(), option.lower(), source.lower(), order)
		(self.value, self.opttype, self.accessed, self.used) = (value, opttype, accessed, used)

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, strDict(self.__dict__))

	def format_opt(self):
		if '!' in self.section:
			return '<%s> %s' % (self.section.replace('!', ''), self.option)
		return '[%s] %s' % (self.section, self.option)

	def format(self, printSection = False, printDefault = False, default = noDefault, source = '', wraplen = 33):
		if (self.value == noDefault) or (not printDefault and (self.value == default)):
			return ''
		if printSection:
			prefix = '[%s] %s' % (self.section, self.option)
		else:
			prefix = self.option
		prefix += ' %s' % self.opttype

		line_list = lfilter(lambda x: x != '', imap(str.strip, self.value.strip().splitlines()))
		if not line_list:
			line_list = [prefix] # just prefix - without trailing whitespace
		elif len(line_list) > 1:
			line_list = [prefix] + line_list # prefix on first line - rest on other lines
		else:
			line_list = [prefix + ' ' + line_list[0]] # everything on one line

		result = ''
		for line in line_list:
			if not result: # first line:
				if source and (len(line) >= wraplen):
					result += '; source: ' + source + '\n'
				elif source:
					result = line.ljust(wraplen) + '  ; ' + source + '\n'
					continue
			else:
				result += '\t'
			result += line + '\n'
		return result.rstrip()

	def _processEntries(cls, entryList):
		result = None
		used = []
		for entry in entryList:
			def mkNew(value):
				return ConfigEntry(entry.section, entry.option, value, '=', '<processed>')
			if entry.opttype == '=': # Normal, overwriting setting
				used = [entry]
				result = entry
			elif entry.opttype == '?=': # Conditional setting
				if not result:
					used = [entry]
					result = entry
			elif entry.opttype == '*=': # this option can not be changed by other config entries
				# TODO: notify that subsequent config options will be ignored
				entry.used = True
				return (entry, [entry])
			elif entry.opttype == '+=':
				used.append(entry)
				if not result: # Use value if currently nothing is set
					result = entry
				else: # Appending value to current value
					result = mkNew(result.value + '\n' + entry.value)
			elif entry.opttype == '^=':
				used.append(entry)
				if not result: # Use value if currently nothing is set
					result = entry
				else: # Prepending value to current value
					result = mkNew(entry.value + '\n' + result.value)
			elif entry.opttype == '-=':
				if entry.value.strip() == '': # without arguments: replace by default
					used = [entry]
					result = None
				elif result: # with arguments: remove string from current value
					used.append(entry)
					result = mkNew(result.value.replace(entry.value.strip(), ''))
				else:
					raise ConfigError('Unable to substract "%s" from non-existing value!' % entry.format_opt())
		return (result, used)
	_processEntries = classmethod(_processEntries)

	def simplifyEntries(cls, entryList):
		(result_base, used) = cls.processEntries(entryList)
		# Merge subsequent += and ^= entries
		def mergeSubsequent(entries):
			previousEntry = None
			for entry in entries:
				if previousEntry and (entry.opttype == previousEntry.opttype):
					if entry.opttype == '+=':
						entry.value = previousEntry.value + '\n' + entry.value
						entry.source = '<processed>'
					elif entry.opttype == '^=':
						entry.value = entry.value + '\n' + previousEntry.value
						entry.source = '<processed>'
					else:
						yield previousEntry
				previousEntry = entry
			if previousEntry:
				yield previousEntry
		if used[0].opttype == '=':
			result = [cls.combineEntries(used)]
		else:
			result = list(mergeSubsequent(used))
		(result_simplified, used_simplified) = cls.processEntries(result)
		assert(len(used_simplified) == len(result))
		assert(result_simplified.value.strip() == result_base.value.strip())
		return result
	simplifyEntries = classmethod(simplifyEntries)

	def processEntries(cls, entryList):
		entryList = list(entryList)
		for entry in entryList:
			entry.accessed = True
		return cls._processEntries(entryList)
	processEntries = classmethod(processEntries)

	def combineEntries(cls, entryList):
		(result, used) = cls.processEntries(entryList)
		for entry in used:
			entry.used = True
		return result
	combineEntries = classmethod(combineEntries)


class ConfigContainer(object):
	def __init__(self, name):
		self.enabled = True
		self._read_only = False
		self._counter = 0
		self._content = {}
		self._content_default = {}

	def setReadOnly(self):
		self._read_only = True

	def getDefault(self, entry):
		return self._content_default.get(entry.option, {}).get(entry.section)

	def setDefault(self, entry):
		curEntry = self.getDefault(entry)
		if self._read_only and not curEntry:
			raise APIError('Config container is read-only!')
		elif curEntry and (curEntry.value != entry.value):
			raise APIError('Inconsistent default values! (%r != %r)' % (curEntry.value, entry.value))
		entry.order = 0
		self._content_default.setdefault(entry.option, {}).setdefault(entry.section, entry)

	def append(self, entry):
		if self._read_only:
			raise APIError('Config container is read-only!')
		self._counter += 1
		entry.order = self._counter
		self._content.setdefault(entry.option, []).append(entry)

	def getEntry(self, option, filterExpr):
		return ConfigEntry.combineEntries(self.getEntries(option, filterExpr))

	def getEntries(self, option, filterExpr):
		entryChain = ichain([self._content.get(option, []), self._content_default.get(option, {}).values()])
		return ifilter(filterExpr, entryChain)

	def getKeys(self):
		return sorted(set(ichain([self._content.keys(), self._content_default.keys()])))
