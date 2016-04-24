import sys

__author__ = "Johannes Koester"

class Interval:
	""" Container for an interval with start and end point. """
	def __init__(self, start, end):
		self.start = start
		self.end = end

	def is_overlap(self, other):
		""" Return True if this interval overlaps with the given interval. """
		return (self.start - other.end <= 0 and self.end - other.start >= 0) or (self.end - other.start >= 0 and self.start - other.end <= 0)
	
	def __repr__(self):
		return "({},{})".format(self.start, self.end)

class IntervalNode:
	"""
	Node in the IntervalTree.
	"""
	def __init__(self, interval, obj, tree):
		self.interval = interval
		self.obj = obj
		self.right = None
		self.left = None
		self.maxend = self.interval.end
		self.height = 0
		self.tree = tree

	def recalc_maxend(self):
		self.maxend = self.interval.end
		if child in (self.left, self.right):
			if child:
				self.maxend = max(child.maxend, self.maxend)

	def __repr__(self):
		return str(self.interval)

class IntervalTree:
	"""
	Interval tree as proposed by Cormen et al.
	"""
	def __init__(self):
		self.root = None

	def insert(self, *args, obj = None):
		"""
		Insert a new interval into the tree. *args can be a start and endpoint given as ints, or a single object with the attributes start and end.
		"""
		node = self._convert_args(*args, obj = obj, node = True)
		self._insert(self.root, node)
		# balance the tree to avoid degeneration
		self._rotate()

	def find(self, *args):
		"""
		Find all intervals in the tree that intersect with the given interval. *args can be a start and endpoint given as ints, or a single object with the attributes start and end.
		"""
		for interval in self._find(self.root, self._convert_args(*args)):
			yield interval

	def _insert(self, root, node):
		if not root:
			self.root = node
			return
		maxend = None
		if node.interval.start < root.interval.start:
			if root.left:
				maxend = self._insert(root.left, node)
			else:
				root.left = node
		else:
			if root.right:
				maxend = self._insert(root.right, node)
			else:
				root.right = node

		root.height += 1		
		
		if not maxend:
			maxend = node.interval.end

		root.maxend = max(maxend, root.maxend)
		return root.maxend

	def _find(self, root, interval):
		if not root:
			return

		if interval.start > root.maxend:
			return

		if root.interval.is_overlap(interval):
			yield root.interval

		if interval.start < root.interval.start:
			for i in self._find(root.left, interval):
				yield i

		elif not interval.end < root.interval.start:
			for i in self._find(root.right, interval):
				yield i

	def _rotate(self):
		if self.root.right and self.root.left:
			heightdiff = self.root.right.height - self.root.left.height
			if heightdiff > 1:
				# perform a left rotation
				p = self.root
				q = self.root.right
				self.root = q
				p.right = q.left
				q.left = p
				q.height += 1
				p.height -= 1

				p.recalc_maxend()
				q.recalc_maxend()
			elif heightdiff < -1:
				# perform a right rotation
				p = self.root
				q = self.root.left
				self.root = q
				p.left = q.right
				q.right = p
				q.height += 1
				p.height -= 1
				
				p.recalc_maxend()
				q.recalc_maxend()

			
			
			
	
	def _inorder(self, root):
		if not root:
			return

		for i in self._inorder(root.left):
			yield i

		yield root

		for i in self._inorder(root.right):
			yield i

	def __iter__(self):
		for i in self._inorder(self.root):
			yield i

	def __repr__(self):
		return ", ".join(map(str, self))
		
	def _convert_args(self, *args, obj = None, node = False):
		""" Convert args into an interval. *args can be a start and endpoint given as ints, or a single object with the attributes start and end. """
		if len(args) == 2:
			interval = Interval(*args)
		else:
			interval =  Interval(args[0].start, args[0].end)
		if node:
			if not obj and len(args) == 1:
				obj = args[0]
			return IntervalNode(interval, obj, self)
		return interval
