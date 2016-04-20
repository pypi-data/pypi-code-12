from collections import OrderedDict
from . import link


class Node:
    def __init__(self, label, x=0.0, y=0.0, z=0.0):
        self.__label = label
        self.__links = {}
        self.__x = x
        self.__y = y
        self.__z = z

    def label(self):
        """
        Returns the label of the node
        :return:str
        """
        return self.__label

    def position(self):
        return self.__x, self.__y, self.__z

    def set_position(self, x=None, y=None, z=None):
        if x is not None:
            self.__x = x
        if y is not None:
            self.__y = y
        if z is not None:
            self.__z = z

    def links(self):
        """
        Returns the links of the node
        :return:list
        """
        return OrderedDict(self.__links)

    def nearest(self, exclude=[]):
        links = self.links()
        nearest = (None, float('inf'))
        for link_label, link in links.items():
            current_weight = link.weight()
            if current_weight < nearest[1] and link_label not in exclude:
                nearest = (link.destination(), current_weight)
        return nearest

    def set_label(self, label):
        """
        Changes the label of the node
        :param label: str
        """
        self.__label = label

    def link_to(self, node, weight):
        """
        Generates a link with another node
        :param node: izigraph.node.Node
        :param weight: int or float
        :return:izigraph.link.Link
        """
        if self.is_linked_to(node):
            raise Exception("Nodes are already linked")
        l = link.Link(self, node, weight)
        self.__links[str(node.label())] = l
        return l

    def is_linked_to(self, node):
        """
        Checks if the current node has a link wiht another node
        :param node: izigraph.node.Node
        :return:boolean
        """
        if str(node.label()) in self.__links:
            return True
        return False

    def get_link(self, node):
        """
        Returns the link between the current node and the other node
        :param node: izigraph.node.Node
        :return:izigraph.link.Link
        """
        if self.is_linked_to(node):
            return self.__links[node.label()]
        return None

    def unlink_from(self, node):
        """
        Removes the link between the current node and another node
        :param node: izigraph.node.Node
        """
        if self.is_linked_to(node):
            del self.__links[node.label()]
        else:
            raise Exception("Nodes are not linked")
