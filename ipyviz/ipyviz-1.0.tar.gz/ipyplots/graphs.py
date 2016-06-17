import networkx as nx
from networkx.readwrite import json_graph
import json
from IPython.display import HTML
from string import Template
import os
import sys
import numpy
import networkx

def graph_plot(adjacency_matrix: numpy.ndarray):
    """
    Creates a JavaScript Graph Plot from the graph given by the adjacency matrix

    :param adjacency_matrix: The adjacency matrix of the graph to be plotted
    :type adjacency_matrix: :class:`numpy.ndarray`
    :return: The IPython HTML output
    :rtype: :class:`IPython.display.HTML`
    """
    g = nx.from_numpy_matrix(adjacency_matrix)
    return nx_graph_plot(g)


def nx_graph_plot(nx_graph: networkx.classes.Graph):
    """
    Creates a JavaScript Graph Plot from the given networkx graph

    :param nx_graph: The graph to be plotted
    :type nx_graph: :func:`networkx.Graph`
    :return: The IPython HTML output
    :rtype: :class:`IPython.display.HTML`
    """
    data = json_graph.node_link_data(nx_graph)
    s = json.dumps(data)
    d = os.path.dirname(sys.modules['ipyplots'].__file__)

    html_content = open(os.path.join(d, 'graph.html'), 'r').read()

    template = Template(html_content)
    return HTML(template.substitute(json=s))
