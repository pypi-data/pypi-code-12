from izigraph.importers import BaseImporter
from izigraph import Graph


class NgvImporter(BaseImporter):

    def import_graph(self, to_import):
        g = Graph(node_label_format="{0}", directed=False)
        nodes, links = self.__get_parsed_graph_parameters(to_import)
        for node in nodes:
            g.add_node(x=node[0], y=node[1])
        for link in links:
            g.link_nodes(link[0], link[1], weight_by_distance=True)
        return g

    def __get_parsed_graph_parameters(self, filename):
        parameters = self.__get_graph_parameters(filename)
        nodes_count = int(parameters[0])
        link_count = 0
        nodes = []
        links = []
        if len(parameters) > 1:
            link_count = int(parameters[1])
        first_node_index = 2
        last_node_index = first_node_index + nodes_count
        for node_index in range(first_node_index, last_node_index):
            nodes_raw_str = parameters[node_index]
            nodes_str = nodes_raw_str.replace(",", ".").split(";")
            node_position = (float(nodes_str[0]), float(nodes_str[1]))
            nodes.append(node_position)
        first_link_index = last_node_index
        last_link_index = first_link_index + link_count
        for link_index in range(first_link_index, last_link_index):
            links_raw_str = parameters[link_index]
            links_list = links_raw_str.split(";")
            links_tuple = (links_list[0], links_list[1])
            links.append(links_tuple)
        return nodes, links

    def __get_graph_parameters(self, filename):
        graph_str = self.__get_string_from_file(filename)
        parameters = graph_str.split("\n")
        return [p for p in parameters if not p == ""]

    def __get_string_from_file(self, filename):
        with open(filename, "r") as f:
            result = f.read()
        return result
