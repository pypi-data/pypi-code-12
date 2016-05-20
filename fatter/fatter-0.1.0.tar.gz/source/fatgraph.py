
''' '''

import fatter

from itertools import combinations
try:
	from Queue import Queue
except ImportError:
	from queue import Queue

def norm(edge):
	return str(edge) if edge >= 0 else '~' + str(~edge)

class FatGraph(object):
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
		return FatGraph([tuple(reversed(vertex)) for vertex in self])
	
	def is_isomorphic_to(self, other):
		if sorted(len(vertex) for vertex in self) != sorted(len(vertex) for vertex in other):
			return False
		
		return self.canonical() == other.canonical()
	
	def is_collapsable(self, edge):
		return edge in self.edges and ~edge in self.edges and self.vertex_lookup[edge] != self.vertex_lookup[~edge]
	
	def collapse(self, edge):
		''' Return a new FatGraph with this edge collapsed. '''
		
		assert(self.is_collapsable(edge))
		
		v1, v2 = self.vertex_lookup[edge], self.vertex_lookup[~edge]
		i1, i2 = self.position_lookup[edge], self.position_lookup[~edge]
		
		v_new = v1[:i1] + v2[i2+1:] + v2[:i2] + v1[i1+1:]
		
		return FatGraph(tuple(vertex for vertex in self if vertex != v1 and vertex != v2) + tuple([v_new]))
	
	def all_collapses(self):
		return [edge for edge in self.edges if self.is_collapsable(edge)]
	
	def upper_neighbours(self):
		return [self.collapse(edge) for edge in self.all_collapses()]
	
	def expand(self, start_edge, end_edge):
		
		assert(start_edge != end_edge)
		assert(start_edge in self.edges and end_edge in self.edges)
		assert(self.vertex_lookup[start_edge] == self.vertex_lookup[end_edge])
		assert(len(self.vertex_lookup[start_edge]) > 3)
		
		v = self.vertex_lookup[start_edge]
		i1, i2 = self.position_lookup[start_edge], self.position_lookup[end_edge]
		i1, i2 = list(sorted([i1, i2]))  # Make sure i1 < i2.
		
		new_edge = max(self.edges) + 1
		v1, v2 = v[i1:i2] + tuple([new_edge]), v[i2:] + v[:i1] + tuple([~new_edge])
		assert(len(v1) >= 3)
		assert(len(v2) >= 3)
		
		return FatGraph(tuple(vertex for vertex in self if vertex != v) + tuple([v1, v2]))
	
	def all_expansions(self):
		return [
			(vertex[i], vertex[j])
			for vertex in self for i, j in combinations(range(len(vertex)), r=2)
			if j - i > 1 and i + len(vertex) - j > 1
			]
	
	def lower_neighbours(self):
		return [self.expand(start_edge, end_edge) for start_edge, end_edge in self.all_expansions()]
	
	def canonical(self, preserve_orientation=False):
		# Use Ben's form.
		
		graphs = [self] if preserve_orientation else [self, self.mirror()]
		
		best_vertices = None
		for graph in graphs:
			for start in graph.edges:
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
							labels[~new_edge] = ~counter
							counter += 1
							queue.put(new_edge)
							if ~new_edge in graph.edges:
								queue.put(~new_edge)
				
				new_vertices = [tuple(labels[edge] for edge in vertex) for vertex in graph]
				ordered_vertices = tuple(sorted(tuple(min(vertex[i:] + vertex[:i] for i in range(len(vertex))) for vertex in new_vertices)))
				
				if best_vertices is None or ordered_vertices < best_vertices:
					best_vertices = ordered_vertices
		
		return FatGraph(best_vertices)
	
	def level(self):
		return sum(len(vertex) - 3 for vertex in self)

