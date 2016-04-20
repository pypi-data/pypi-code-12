from uuid import uuid4
from . import link


class Node:
    def __init__(self, label):
        self.__label = label
        self.__id = uuid4()
        self.__links = dict()

    def label(self):
        """
        Returns the label of the node
        :return:str
        """
        return self.__label

    def id(self):
        """
        Returns the od of the node
        :return:uuid.UUID
        """
        return self.__id

    def links(self):
        """
        Returns the links of the node
        :return:list
        """
        return self.__links

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
        self.__links[str(node.id())] = l
        return l

    def is_linked_to(self, node):
        """
        Checks if the current node has a link wiht another node
        :param node: izigraph.node.Node
        :return:boolean
        """
        if str(node.id()) in self.__links:
            return True
        return False

    def get_link(self, node):
        """
        Returns the link between the current node and the other node
        :param node: izigraph.node.Node
        :return:izigraph.link.Link
        """
        if self.is_linked_to(node):
            return self.__links[str(node.id())]
        return None

    def unlink_from(self, node):
        """
        Removes the link between the current node and another node
        :param node: izigraph.node.Node
        """
        if self.is_linked_to(node):
            del self.__links[str(node.id())]
        else:
            raise Exception("Nodes are not linked")
