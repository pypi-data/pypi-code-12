
''' '''

import fatter

import string
from math import log
from itertools import combinations
try:
	from Queue import Queue
except ImportError:
	from queue import Queue

def norm(edge):
	return str(edge) if edge >= 0 else '~' + str(~edge)

class FatGraph(object):
	''' This represents a fat graph.
	
	This is given by a list of vertices, each of which is specified by a list of incident edges.
	The vertices can be given in any order. The edges of a vertex must be given in cyclic order.
	The (directed) edges are labelled by integers and if an edge is labelled x then its inverse
	is labelled ~x.
	
	Edges are not required to have an inverse. In which case in the dual polygonalisation the
	edge corresponds to a section of a boundary component of the surface. '''
	def __init__(self, vertices):
		self.vertices = tuple(sorted(tuple(min(vertex[i:] + vertex[:i] for i in range(len(vertex))) for vertex in vertices)))
		self.edges = [edge for vertex in self for edge in vertex]
		
		self.vertex_lookup = dict((edge, vertex) for vertex in self for edge in vertex)
		self.neighbour_lookup = dict((edge, neighbour) for vertex in self for (edge, neighbour) in zip(vertex, vertex[1:] + vertex[:1]))
		self.position_lookup = dict((edge, index) for vertex in self for index, edge in enumerate(vertex))
	def __str__(self):
		return '[' + ', '.join('(' + ', '.join(norm(edge) for edge in vertex) + ')' for vertex in self) + ']'
	def __repr__(self):
		return str(self)
	def __eq__(self, other):
		return self.vertices == other.vertices
	def __ne__(self, other):
		return not (self == other)
	def __iter__(self):
		return iter(self.vertices)
	def __hash__(self):
		return hash(self.vertices)
	def mirror(self):
		''' Return this FatGraph with the reversed orientation. '''
		
		return FatGraph(tuple(tuple(reversed(vertex)) for vertex in self))
	
	def deficiency(self):
		''' Return the maximum number of expansions that can be performed.
		
		This is the same as the number of edges that can be added to the
		dual polygonalisation before it becomes a triangulation. '''
		
		return sum(len(vertex) - 3 for vertex in self)
	
	def is_isomorphic_to(self, other):
		''' Return if this FatGraph is isomorphic to the other FatGraph. '''
		
		# Start with some cheap isomorphism invariants.
		if sorted(len(vertex) for vertex in self) != sorted(len(vertex) for vertex in other):
			return False
		
		return self.canonical() == other.canonical()
	
	def is_collapsable(self, edge):
		''' Return if this edge can be collapsed.
		
		It is collapsable if and only if it is connnected to a different vertex. '''
		
		return edge in self.edges and ~edge in self.edges and self.vertex_lookup[edge] != self.vertex_lookup[~edge]
	
	def collapse(self, edge):
		''' Return a new FatGraph with this edge collapsed. '''
		
		assert(self.is_collapsable(edge))
		
		v1, v2 = self.vertex_lookup[edge], self.vertex_lookup[~edge]
		i1, i2 = self.position_lookup[edge], self.position_lookup[~edge]
		
		v_new = v1[:i1] + v2[i2+1:] + v2[:i2] + v1[i1+1:]
		
		return FatGraph(tuple(vertex for vertex in self if vertex != v1 and vertex != v2) + tuple([v_new]))
	
	def all_collapses(self):
		''' Return a list of all the different collapses that can be performed. '''
		
		return [edge for edge in self.edges if self.is_collapsable(edge)]
	
	def upper_neighbours(self):
		''' Return a list of all the FatGraphs that can be obtained by performing a collapse of self.
		
		These all have deficiency equal to self.deficiency() + 1. '''
		
		return [self.collapse(edge) for edge in self.all_collapses()]
	
	def expand(self, start_edge, end_edge):
		''' Return the FatGraph obtained by expanding open a vertex.
		
		The expansion is done by partitioning the half-edges at the vertex into two,
		determined by start_edge and end_edge. These are then used to form
		two new vertices and a new edge is added between them. Collapsing this
		new edge results in the original FatGraph.
		
		start_edge and end_edge must be distinct and must both be at the same vertex.
		Additionally, there must be at least two half-edges in each partition. '''
		
		assert(start_edge != end_edge)
		assert(start_edge in self.edges and end_edge in self.edges)
		assert(self.vertex_lookup[start_edge] == self.vertex_lookup[end_edge])
		
		v = self.vertex_lookup[start_edge]
		i1, i2 = list(sorted([self.position_lookup[start_edge], self.position_lookup[end_edge]]))  # Make sure i1 < i2.
		
		new_edge = max(self.edges) + 1
		v1, v2 = v[i1:i2] + tuple([new_edge]), v[i2:] + v[:i1] + tuple([~new_edge])
		assert(len(v1) >= 3)
		assert(len(v2) >= 3)
		
		return FatGraph(tuple(vertex for vertex in self if vertex != v) + tuple([v1, v2]))
	
	def all_expansions(self):
		''' Return a list of all the different expansions that can be performed. '''
		
		return [
			(vertex[i], vertex[j])
			for vertex in self for i, j in combinations(range(len(vertex)), r=2)
			if j - i > 1 and i + len(vertex) - j > 1
			]
	
	def lower_neighbours(self):
		''' Return a list of all the FatGraphs that can be obtained by performing an expansion of self.
		
		These all have deficiency equal to self.deficiency() - 1. '''
		
		return [self.expand(start_edge, end_edge) for start_edge, end_edge in self.all_expansions()]
	
	def neighbours(self):
		''' Return a list of all the FatGraphs that can be obtained by performing a collapse or expansion of self.
		
		These all have deficiency equal to self.deficiency() +/- 1. '''
		
		return self.lower_neighbours() + self.upper_neighbours()
	
	def canonical(self, preserve_orientation=False):
		''' Return this FatGraph with a canonical labelling.
		
		We follow the idea of Ben Burton's isomorphism signature here. We pick a
		starting point and assign labels by performing a breadth first traversal.
		We repeat this for each starting point and use the one that results in the
		lexicographically first ordering. '''
		
		# We need to consider self with the reversed orientation if we want a
		# canonical form that is invariant under orientation reversing isomorphisms.
		graphs = [self] if preserve_orientation else [self, self.mirror()]
		
		best_vertices = None
		for graph in graphs:  # For each graph.
			for start in graph.edges:  # For each starting position.
				labels = dict()
				queue = Queue()
				
				labels[start] = 0
				queue.put(start)
				if ~start in graph.edges:
					labels[~start] = ~0
					queue.put(~start)
				counter = 1
				while not queue.empty():
					edge = queue.get()
					vertex = graph.vertex_lookup[edge]
					index = graph.position_lookup[edge]
					
					for new_edge in vertex[index:] + vertex[:index]:
						if new_edge not in labels:
							labels[new_edge] = counter
							if ~new_edge in graph.edges:
								labels[~new_edge] = ~counter
								queue.put(~new_edge)
							counter += 1
				
				new_vertices = [tuple(labels[edge] for edge in vertex) for vertex in graph]
				ordered_vertices = tuple(sorted(tuple(min(vertex[i:] + vertex[:i] for i in range(len(vertex))) for vertex in new_vertices)))
				
				if best_vertices is None or ordered_vertices < best_vertices:
					best_vertices = ordered_vertices
		
		return FatGraph(best_vertices)
	
	def canonical_string(self):
		''' Return a compress string form of self.canonical(). '''
		
		char = string.lowercase + string.uppercase + string.digits  # Available characters.
		start_char = string.lowercase  # Available first characters.
		
		def to_string(number):
			''' Return number as a string.
			
			We use the format:
			  [start_char][char]*
			where the first character represents the least significant place.
			
			If the number is negative then we return to_string(~number) with
			the first character's case swapped. '''
			
			pos = number >= 0
			if not pos: number = ~number
			
			start = start_char[number % len(start_char)]
			number = number // len(start_char)
			strn = [start if pos else start.swapcase()]
			while number != 0:
				strn.append(char[number % len(char)])
				number = number // len(char)
			
			return ''.join(strn)
		
		canonical = self.canonical()
		
		digits = 1 if len(canonical.edges) <= len(start_char) else int(log(len(canonical.edges) // len(start_char)) / log(len(char))) + 1
		char_start = char[digits-1]
		char_self = '~'.join(''.join(to_string(edge) for edge in vertex) for vertex in self)
		
		return char_start + '~' + char_self

