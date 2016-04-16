from . import node


class Graph:
    def __init__(self, label='default_graph', node_label_format='node_{0}'):
        self.__label = label
        self.__nodes = dict()
        self.__new_node_index = 0
        self.__node_label_format = node_label_format

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
        return self.__nodes

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
        if label in self.__nodes:
            raise Exception('A node with the label {0} already exists in graph {1}'.format(label, self.__label))
        n = node.Node(label, x=x, y=y)
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

    def link_nodes(self, source, destination, weight=1, weights=[1, 1], bidirectional=False):
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
            if not isinstance(weights, list) and len(weights) != 2:
                raise ValueError('weights must be a list of two elements')
            return source.link_to(destination, weights[0]), destination.link_to(source, weights[1])
        return source.link_to(destination, weight=weight)

    def node_belongs_to_graph(self, n):
        if isinstance(n, str):
            return n in self.__nodes
        elif isinstance(n, node.Node):
            return n.label() in self.__nodes
        raise ValueError('n must be an instance of string or izigraph.node.Node')

    def validate_node(self, n):
        if not isinstance(n, node.Node):
            raise ValueError('node must be a izigraph.Node instance')
        if not self.node_belongs_to_graph(n):
            raise Exception('node doesn\'t belongs to graph {0}'.format(self.__label))

    def nodes_are_linked(self, na, nb):
        if isinstance(na, str):
            na = self.find_node_by_label(na)
        if isinstance(nb, str):
            nb = self.find_node_by_label(nb)
        self.validate_node(na)
        self.validate_node(nb)
        return na.is_linked_to(nb)

    @staticmethod
    def create_from_dict(config):
        if not isinstance(config, dict):
            raise ValueError('The config variable must be an instance of dict')
        if 'nodes' not in config:
            raise Exception('The config dictionary must have a \'nodes\' key')
        if not isinstance(config['nodes'], int) or config['nodes'] <= 0:
            raise ValueError('The nodes key must contain an integer > 0')
        if 'links' in config and not isinstance(config['links'], dict):
            raise ValueError('The links key must be a list')
        n_l_f = 'node_{0}'
        if 'node_label_format' in config:
            n_l_f = config['node_label_format']
        g = Graph(node_label_format=n_l_f)
        if 'label' in config:
            g.set_label(config['label'])
        g.add_nodes(config['nodes'])
        if 'links' in config:
            links = config['links']
            for node_label in links:
                n = g.find_node_by_label(node_label)
                if n is None:
                    raise Exception('Node {0} not found in graph {1}', node_label, Graph.__label)
                node_links = links[node_label]
                for node_link in node_links:
                    w = 1
                    if 'weight' in node_link:
                        w = node_link['weight']
                    if 'destination' not in node_link:
                        raise Exception('The linkl must have a \'destination\' key')
                    g.link_nodes(node_label, node_link['destination'], weight=w)
        return g
