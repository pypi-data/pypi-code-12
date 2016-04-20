from . import node
import uuid


class Graph:
    def __init__(self, label='default_graph'):
        self.__label = label
        self.__nodes = dict()
        self.__nodes_labels = dict()

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

    def find_node_by_id(self, node_id):
        """
        :param node_id: Must be an instance of uuid.UUID or string. Allows to find the node in the nodes dictionary.
        :return: izigraph.node.Node or None
        """
        if isinstance(node_id, uuid.UUID):
            node_id = str(node_id)
        if not isinstance(node_id, str):
            raise ValueError('node_id must be an instance of str or uuid.UUID')
        if node_id in self.__nodes:
            return self.__nodes[node_id]
        return None

    def find_node_by_label(self, label):
        """
        :param label: The label string to search in the nodes_label dictionary
        :return: izigraph.node.Node or None
        """
        if not isinstance(label, str):
            raise ValueError('Label must be an instance of str')
        if label not in self.__nodes_labels:
            return None
        else:
            return self.find_node_by_id(self.__nodes_labels[label])

    def add_node(self, label):
        """
        :param label: The label string of the node to be added
        :return:The added node
        """
        if label in self.__nodes_labels:
            raise Exception('A node with the label %s already exists in graph %s'.format(label, self.__label))
        n = node.Node(label)
        self.__nodes[str(n.id())] = n
        self.__nodes_labels[n.label()] = str(n.id())
        return n

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
        if not isinstance(source, node.Node):
            raise ValueError('Source node must be a izigraph.Node instance')
        if not isinstance(destination, node.Node):
            raise ValueError('Destination node must be a izigraph.Node instance')
        if str(source.id()) not in self.__nodes:
            raise Exception('Source node must be a part of graph %s'.format(self.__label))
        if str(destination.id()) not in self.__nodes:
            raise Exception('Destination node must be a part of graph %s'.format(self.__label))
        if bidirectional:
            if not isinstance(weights, list) and len(weights) != 2:
                raise ValueError('weights must be a list of two elements')
            return source.link_to(destination, weights[0]), destination.link_to(source, weights[1])
        return source.link_to(destination, weight=weight)
