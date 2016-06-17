import math
from distutils.version import StrictVersion

class BuildDiagramsGraph:

    def __init__(self, diagram_a, diagram_b):
        self._diagram_a = diagram_a
        self._diagram_b = diagram_b

    @classmethod
    def enabled(cls):
        try:
            import igraph
            return StrictVersion('0.6.5') < StrictVersion(igraph.__version__)
        except ImportError:
            return False

    def __call__(self, valid_edge, distance):
        import igraph
        a_size = len(self._diagram_a)
        b_size = len(self._diagram_b)
        graph = igraph.Graph(2*(a_size + b_size)) # groups plus placeholders for diagonal

        def vertex_type(idx):
            if idx < a_size:
                return True
            elif idx >= a_size and idx < a_size + b_size:
                return False
            elif idx >= a_size + b_size and idx < a_size + b_size + a_size:
                return False
            elif idx >= a_size + b_size + a_size and idx < a_size + b_size + a_size + b_size:
                return True
            else:
                raise RuntimeError("Wrong index")

        graph.vs["type"] = map(vertex_type, xrange(len(graph.vs)))
        edges, weights = [], []

        for idx_a in xrange(a_size):
            for idx_b in xrange(b_size):
                good_group = (math.isinf(self._diagram_a[idx_a][1]) ^ math.isinf(self._diagram_b[idx_b][1])) == 0
                if good_group and valid_edge(self._diagram_a[idx_a], self._diagram_b[idx_b]):
                    edges += [(idx_a, a_size + idx_b)]
                    weights.append(distance(self._diagram_a[idx_a], self._diagram_b[idx_b]))

                # diagonal-diagonal always
                edges += [(a_size + b_size + idx_a, a_size + b_size + a_size + idx_b)]
                weights.append(0.0)

        def add_diagonal_projection(diagram, start_index, edges, weights):
            diagonal = lambda ((x, y)): (x, x)
            for idx in xrange(len(diagram)):
                if valid_edge(diagram[idx], diagonal(diagram[idx])):
                    edges += [(start_index + idx, a_size + b_size + start_index + idx)]
                    weights.append(distance(diagram[idx], diagonal(diagram[idx])))

        add_diagonal_projection(self._diagram_a, 0, edges, weights)
        add_diagonal_projection(self._diagram_b, a_size, edges, weights)

        graph.add_edges(edges)
        graph.es["weight"] = weights

        return graph
