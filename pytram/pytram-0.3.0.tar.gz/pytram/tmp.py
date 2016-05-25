

####################################################################################################
#
#   AUXILIARY FUNCTIONS
#
####################################################################################################

def _depth_first_search(graph, node, node_list):
    r"""performs a depth first search"""
    node_list.append(node)
    for j in xrange(graph.shape[0]):
        if (graph[node, j] > 0) and (j not in node_list):
            _depth_first_search(graph, j, node_list)
    node_list.remove(node)
    node_list.append(node)

def _kosaraju(graph):
    r"""finds communication classes via Kosaraju's algorithm"""
    communication_class = []
    explored = []
    unexplored = range(graph.shape[0])
    while len(unexplored) > 0:
        node = unexplored[0]
        _depth_first_search(graph, node, explored)
        unexplored = [node for node in unexplored if node not in explored]
    revisited = []
    while len(explored) > 0:
        node = explored[-1]
        _depth_first_search(graph.transpose(), node, revisited)
        node_list = [node for node in revisited if node in explored]
        communication_class.append(node_list)
        explored = [node for node in explored if node not in revisited]
    return communication_class

    