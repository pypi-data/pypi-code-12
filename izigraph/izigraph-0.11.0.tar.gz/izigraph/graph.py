try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
import izigraph


class Graph:
    def __init__(self, label='default_graph', node_label_format='node_{0}', directed=True):
        self.__label = label
        self.__nodes = {}
        self.__links_dict = {}
        self.__links = []
        self.__new_node_index = 0
        self.__node_label_format = node_label_format
        self.__is_directed = directed

    def label(self):
        """
        :return:The label of the Graph
        """
        return self.__label

    def set_label(self, label):
        """
        Changes the label of the graph
        :param label: string
        """
        self.__label = label

    def nodes(self):
        """
        Return the dictionary of Nodes. The key is the id of the node
        :return: dictionary of nodes
        """
        return OrderedDict(sorted(self.__nodes.items(), key=lambda t: t[0]))

    def links(self):
        return self.__links

    def links_count(self):
        if self.__is_directed:
            return len(self.__links)
        return len(self.__links)/2

    def find_node_by_label(self, label):
        """
        :param label: The label string to search in the nodes_label dictionary
        :return: izigraph.node.Node or None
        """
        if not isinstance(label, str):
            raise ValueError('Label must be an instance of str')
        if label not in self.__nodes:
            return None
        else:
            return self.__nodes[label]

    def add_node(self, x=0.0, y=0.0):
        """
        :return:The added node
        """
        label = self.__node_label_format.format(self.__new_node_index)
        n = izigraph.Node(label, x=x, y=y)
        self.__nodes[n.label()] = n
        self.__new_node_index += 1
        return n

    def add_nodes(self, nodes):
        for i in range(self.__new_node_index, self.__new_node_index + nodes):
            self.add_node()

    def nodes_count(self):
        """
        :return:The size of the nodes dictionary
        """
        return len(self.__nodes)

    def link_nodes(self, source, destination, weight=1, weights=None, bidirectional=False):
        """
        :param source: izigraph.node.Node
        :param destination: izigraph.node.Node
        :param weight: int
        :param weights: list of int
        :param bidirectional: boolean
        :return:izigraph.link.Link or tuple of izigraph.link.Link
        """
        if isinstance(source, str):
            source = self.find_node_by_label(source)
        if isinstance(destination, str):
            destination = self.find_node_by_label(destination)
        self.validate_node(source)
        self.validate_node(destination)
        if bidirectional:
            if weights is None:
                weights = [1, 1]
            if not isinstance(weights, list) and len(weights) != 2:
                raise ValueError('weights must be a list of two elements')
            s_d_link = izigraph.Link(source, destination, weight=weights[0])
            d_s_link = izigraph.Link(destination, source, weight=weights[1])
            self.__links.append(s_d_link)
            self.__links.append(d_s_link)
            self.__links_dict[(source.label(), destination.label())] = s_d_link
            self.__links_dict[(destination.label(), source.label())] = d_s_link
            return s_d_link, d_s_link
        s_d_link = izigraph.Link(source, destination, weight=weight)
        self.__links_dict[(source.label(), destination.label())] = s_d_link
        self.__links.append(s_d_link)
        if not self.__is_directed:
            self.__links_dict[(destination.label(), source.label())] = izigraph.Link(destination, source, weight=weight)
            self.__links.append(self.__links_dict[(destination.label(), source.label())])
        return s_d_link

    def node_belongs_to_graph(self, n):
        if isinstance(n, str):
            return n in self.__nodes
        elif isinstance(n, izigraph.Node):
            return n.label() in self.__nodes
        raise ValueError('n must be an instance of string or Node')

    def validate_node(self, n):
        if not isinstance(n, izigraph.Node):
            raise ValueError('node must be a izigraph.Node instance')
        if not self.node_belongs_to_graph(n):
            raise Exception('node doesn\'t belongs to graph {0}'.format(self.__label))

    def nodes_are_linked(self, source, destination):
        if isinstance(source, str):
            source = self.find_node_by_label(source)
        if isinstance(destination, str):
            destination = self.find_node_by_label(destination)
        return (source.label(), destination.label()) in self.__links_dict

    def get_link(self, source, destination):
        if isinstance(source, str):
            source = self.find_node_by_label(source)
        if isinstance(destination, str):
            destination = self.find_node_by_label(destination)
        if not self.nodes_are_linked(source, destination):
            return None
        return self.__links_dict[(source.label(), destination.label())]

    def is_directed(self):
        return self.__is_directed

    def links_dict(self):
        return self.__links_dict
