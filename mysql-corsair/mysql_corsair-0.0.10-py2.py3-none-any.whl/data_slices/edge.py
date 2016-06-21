class Edge:
    def __init__(self, fk):
        self.source_table = fk.source_table
        self.source_column = fk.source_column
        self.target_table = fk.target_table
        self.target_column = fk.target_column
        self.node_names = set([self.source_table, self.target_table])

    # Useful for set containment
    def __eq__(self, other_edge):
        return (self.node_names == other_edge.node_names)

    def to_string(self):
        return "({0}, {1})".format(self.source_table, self.target_table)


class EdgeSet:
    def __init__(self):
        self.edges = []

    def add(self, edge):
        self.edges.append(edge)

    def __contains__(self, candidate_edge):
        for edge in self.edges:
            if edge.__eq__(candidate_edge):
                return True
        return False
