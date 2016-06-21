
''' '''

import straighter

from math import log
from fractions import gcd
try:
	from Queue import Queue
except ImportError:
	from queue import Queue


class Terminal(object):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return 'T' + str(self.value)
	def __repr__(self):
		return str(self)
	def __eq__(self, other):
		return isinstance(other, Terminal) and self.value == other.value
	def __ne__(self, other):
		return not (self == other)
	def __hash__(self):
		return hash(self.value)

class NonTerminal(object):
	def __init__(self, name):
		self.name = str(name)
	def __str__(self):
		return 'N' + str(self.name)
	def __repr__(self):
		return str(self)


def inverse_dag(delta):
	images = set([image for item in delta for image in delta[item]])
	
	# Start by rebuilding the inverse.
	inverse = dict((item, set()) for item in images)
	for item in delta:
		for image in delta[item]:
			inverse[image].add(item)
	
	return inverse


class StraightLineProgram(object):
	''' This represents a stright line program. '''
	def __init__(self, delta, root, levels):
		self.delta = delta
		self.root = root
		# If w in self.delta[v] then self.labels[w] < self.labels[v].
		self.levels = levels
		
		self.depth = self.levels[self.root]
		
		self.images = set([image for item in self.delta for image in self.delta[item]])
		self.sources = set(self.delta) - self.images
		self.sinks = self.images - set(self.delta)  # == set(Terminals).
		
		assert(self.depth >= 1)
		# Cache for later.
		self._lengths = None
		self._inverse = None
	
	@classmethod
	def from_dict(self, delta, root=None):
		# Map all of the non-terminal states to vertices with the same name.
		mapping = {image: Terminal(image) for images in delta.values() for image in images if image not in delta}
		mapping.update({value: NonTerminal(value) for value in delta})
		
		# Use the mapping to rebuild the delta map.
		delta = dict((mapping[key], [mapping[image] if image in mapping else image for image in value]) for key, value in delta.items())
		
		images = set([image for item in delta for image in delta[item]])
		sources = set(delta) - images
		sinks = images - set(delta)
		
		# Find the root.
		if root is None:
			if len(sources) == 1:
				root = sources.pop()
			else:
				raise ValueError('Root not unique, please specify one.')
		else:
			root = mapping[root]
		
		# Build the levels.
		inverse = inverse_dag(delta)
		
		levels = dict((sink, 0) for sink in sinks)
		check, next_check = set([item for sink in sinks for item in inverse[sink]]), set()
		while check:
			for item in check:
				if item not in levels:
					try:
						levels[item] = max(levels[image] for image in delta[item]) + 1
						next_check.update(inverse[item])
					except KeyError:
						pass
			
			check, next_check = next_check, set()
		
		return StraightLineProgram(delta, root, levels)
	
	@classmethod
	def from_list(self, items):
		root = NonTerminal(0)
		items = [Terminal(item) for item in items]
		
		delta = {root: items}
		levels = {root: 1}
		levels.update({item: 0 for item in items})
		
		return StraightLineProgram(delta, root, levels)
	
	def copy(self):
		return self.product('')
	
	def __call__(self, item):
		return self.delta[item]
	def inverse(self):
		if self._inverse is None:
			self._inverse = inverse_dag(self.delta)
		return self._inverse
	def __str__(self):
		return str(list(self))
	def __repr__(self):
		strn = []
		for item in sorted(self.delta, key=self.levels.__getitem__, reverse=True):  # Only show the reachable vertices.
			if item not in self.sinks:
				strn.append('%s%s --> %s' % ('*Root* ' if item == self.root else '', item, '.'.join(str(image) for image in self(item))))
		
		return '\n'.join(strn)
	def dot(self):
		strn = ['digraph G {']
		for item in sorted(self.delta, key=self.levels.__getitem__, reverse=True):  # Only show the reachable vertices.
			if item not in self.sinks:
				strn.append('  %s -> {%s}' % (item, ', '.join(str(image) for image in self(item))))
		strn.append('}')
		
		return '\n'.join(strn)
	
	def descendents(self, root=None):
		''' Return the set of vertices reachable from root. '''
		if root is None: root = self.root
		
		seen = set([root])
		this_level, next_level = [root], []
		while this_level:
			for item in this_level:
				if item not in self.sinks:
					for image in self(item):
						if image not in seen:
							next_level.append(image)
							seen.add(image)
			
			this_level, next_level = next_level, []
		
		return seen
	def simplified(self):
		descendents = self.descendents()
		delta = dict((key, value) for key, value in self.delta.items() if key in descendents)
		levels = dict((key, value) for key, value in self.levels.items() if key in descendents)
		return StraightLineProgram(delta, self.root, levels)
	
	def lengths(self):
		if self._lengths is None:
			self._lengths = dict((sink, 1) for sink in self.sinks)
			for item in sorted(self.delta, key=self.levels.__getitem__):
				self._lengths[item] = sum(self._lengths[image] for image in self(item))
		return self._lengths
	def __len__(self):
		return self.lengths()[self.root]
	def size(self):
		return len(self.descendents())
	def __eq__(self, other):
		if len(self) != len(other):  # Cheap test.
			return False
		
		return NotImplemented
	def __ne__(self, other):
		return not (self == other)
	def is_isomorphic_to(self, other):
		#if self.size() != other.size():
		#	return False
		
		mapping = {self.root: other.root}
		queue = Queue()
		queue.put(self.root)
		
		while not queue.empty():
			item = queue.get()
			
			if len(self(item)) != len(other(mapping[item])):
				return False
			
			for image, other_image in zip(self(item), other(mapping[item])):
				if image in mapping:
					if mapping[image] != other_image:
						return False
				else:
					mapping[image] = other_image
					queue.put(item)
		
		return True
	
	def __iter__(self):
		if len(self(self.root)) == 0:
			return
		
		queues = []
		queues.append(Queue())
		for image in self(self.root):
			queues[-1].put(image)
		
		while queues:
			item = queues[-1].get()
			if queues[-1].empty():
				queues.pop()
			if isinstance(item, Terminal):
				yield item.value
			else:
				queues.append(Queue())
				for image in self(item):
					queues[-1].put(image)
		
		return
	
	def __getitem__(self, value):
		if isinstance(value, slice):
			# If this has been done right then:
			#  self[i:j][p:q].is_isomorphic_to(self[i+p:i+q])
			start = 0 if value.start is None else value.start if value.start >= 0 else len(self) + value.start
			stop = len(self) if value.stop is None else value.stop if value.stop >= 0 else len(self) + value.stop
			
			if start == 0 and stop == len(self):
				return self.copy()
			
			value = 0
			blocks = []
			for image in self(self.root):
				block = StraightLineProgram.from_list([image]) if image in self.sinks else StraightLineProgram(self.delta, image, self.levels).simplified()
				if value < start < value + len(block) <= stop:
					blocks.append(block[start-value:])
				elif start < value < stop < value + len(block):
					blocks.append(block[:stop - value])
				elif value <= start < stop < value + len(block):
					blocks.append(block[start-value:stop-value])
				elif start <= value < value + len(block) <= stop:
					blocks.append(block)
				
				value += len(block)
			
			return sum(blocks, [])
		else:  # We are returning a single item.
			if value >= len(self) or value < -len(self):
				raise IndexError('index out of range')
			
			if value < 0: value = len(self) + value
			
			lengths = self.lengths()
			position = self.root
			while value >= 0:
				for image in self(position):
					if lengths[image] > value:
						if value == 0 and image in self.sinks:
							return image
						else:
							position = image
							break
					else:
						value -= lengths[image]
	
	def product(self, other):
		''' Return the SLP in which each non-terminal vertex v has been replaces by the vertex (v, other).
		
		This is useful for forming disjoint unions. '''
		
		mapping = dict((item, NonTerminal(item.name + other) if isinstance(item, NonTerminal) else item) for item in self.levels)
		
		return StraightLineProgram(
			dict((mapping[key], [mapping[image] for image in value]) for key, value in self.delta.items()),
			mapping[self.root],
			dict((mapping[item], self.levels[item]) for item in self.levels)
			)
	def extend(self, items, to_right=True):
		if isinstance(items, StraightLineProgram):
			if len(items) == 0: return
			
			root = NonTerminal(0)
			P = self.product('a')
			Q = items.product('b')
			
			delta = {root: [P.root, Q.root] if to_right else [Q.root, P.root]}
			delta.update(P.delta)
			delta.update(Q.delta)
			levels = {root: max(P.depth, Q.depth) + 1}
			levels.update(P.levels)
			levels.update(Q.levels)
			self.__init__(delta, root, levels)
			return self
		else:
			items = list(items)
			if len(items) == 0: return
			
			if to_right:
				self.delta[self.root] = self.delta[self.root] + items
			else:
				self.delta[self.root] = items + self.delta[self.root]
			
			return self
	def __add__(self, other):
		P = self.copy()
		P.extend(other)
		return P
	def __radd__(self, other):
		P = self.copy()
		P.extend(other, to_right=False)
		return P
	
	def insert(self, item, index):
		''' Modify this SLP to also return item at position index. '''
		if index < 0: index = len(self) + index
		index = min(max(index, 0), len(self))
		
		P = self[:index] + [item] + self[index:]
		
		return self.__init__(P.delta, P.root, P.levels)
	def append(self, item):
		''' Modify this SLP to finish by returning item. '''
		self.insert(item, -1)
		
		# Could also do something like:
		# self.delta[self.root].append(item)
	
	def __mul__(self, other):
		root = NonTerminal(0)
		if other == 0:
			return StraightLineProgram(
				{root: []},
				root,
				{root: 1}
				)
		
		P = self.product('a')
		
		binary = [x == '1' for x in bin(other)[2:]]
		powers = [NonTerminal(len(binary)-i-1) for i in range(len(binary)-1)] + [P.root]
		
		delta = {root: [power for power, use in zip(powers, binary) if use]}
		delta.update({powers[i]: [powers[i+1], powers[i+1]] for i in range(len(binary)-1)})
		delta.update(P.delta)
		levels = {root: P.depth + len(binary)}
		levels.update({powers[i]: P.depth + len(binary) - i - 1 for i in range(len(binary))})
		levels.update(P.levels)
		return StraightLineProgram(delta, root, levels)
	
	def __rmul__(self, other):
		return self * other
	
	def __contains__(self, value):
		return value in self.sinks
	
	def count(self, value,root=None):
		if root is None: root = self.root
		counts = dict((sink, 1 if sink == value else 0) for sink in self.sinks)
		for item in sorted(self.delta, key=self.levels.__getitem__):
			counts[item] = sum(counts[image] for image in self(item))
		return counts[root]
	
	def reverse(self):
		delta = dict((key, list(reversed(value))) for key, value in self.delta.items())
		self.__init__(delta, self.root, self.levels)
	
	def __reversed__(self):
		P = self.copy()
		P.reverse()
		return iter(P)
	
	def bolt_up(self, left, right):
		left, right = set(left), set(right)
		
		delta = dict((item, list(self(item))) for item in self.delta)
		inverse = self.inverse()
		
		for item in sorted(delta, key=self.levels.__getitem__):  # Only show the reachable vertices.
			if item != self.root:
				target = delta[item]
				initial, terminal = target[0], target[-1]
				
				if initial in left and terminal in right and len(target) >= 3:  # [L, ---, R]
					substitute = [initial, item, terminal]
					delta[item] = delta[item][1:-1]
				elif initial in left and terminal in right and len(target) == 2:  # [L, R]
					substitute = [initial, terminal]
					del delta[item]
				elif initial in left and len(target) == 1:  # [L]
					substitute = [initial]
					del delta[item]
				elif terminal in right and len(target) == 1:  # [R]
					substitute = [terminal]
					del delta[item]
				elif initial in left and terminal not in right and len(target) >= 2:  # [L, ---]
					substitute = [initial, item]
					delta[item] = delta[item][1:]
				elif initial not in left and terminal in right and len(target) >= 2:  # [---, R]
					substitute = [item, terminal]
					delta[item] = delta[item][:-1]
				else:  # [---]
					substitute = [item]
				
				for inv in inverse[item]:
					delta[inv] = [image2 for image in delta[inv] for image2 in (substitute if image == item else [image])]
		
		# Build the levels.
		inverse = inverse_dag(delta)
		
		levels = dict((sink, 0) for sink in self.sinks)
		check, next_check = set([item for sink in levels for item in inverse[sink]]), set()
		while check:
			for item in check:
				if item not in levels:
					try:
						levels[item] = max(levels[image] for image in delta[item]) + 1
						next_check.update(inverse[item])
					except KeyError:
						pass
			
			check, next_check = next_check, set()
		
		return StraightLineProgram(delta, self.root, levels)
	
	def pairs(self):
		''' Return all the pairs that appear in self. '''
		
		initial, terminal = dict(), dict()
		pairs = set()
		for item in sorted(self.delta, key=self.levels.__getitem__):  # Only show the reachable vertices.
			images = self(item)
			initial[item] = images[0] if images[0] in self.sinks else initial[images[0]]
			terminal[item] = images[-1] if images[-1] in self.sinks else terminal[images[-1]]
			
			for a, b in zip(images, images[1:]):
				pairs.add((a if a in self.sinks else terminal[a], b if b in self.sinks else initial[b]))
		
		return list(pairs)

