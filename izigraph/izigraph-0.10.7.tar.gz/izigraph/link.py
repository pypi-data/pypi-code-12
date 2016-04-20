from . import node


class Link:
    def __init__(self, source, destination, weight=1):
        if not isinstance(weight, (int, float)):
            raise ValueError
        if not isinstance(source, node.Node) or not isinstance(destination, node.Node):
            raise ValueError
        self.__source = source
        self.__destination = destination
        self.__weight = weight

    def source(self):
        """
        Return the source node
        :return:izigraph.node.Node
        """
        return self.__source

    def destination(self):
        """
        Return the destination node
        :return:izigraph.node.Node
        """
        return self.__destination

    def weight(self):
        """
        Returns the weight of the Link
        :return:izigraph.node.Node
        """
        return self.__weight
