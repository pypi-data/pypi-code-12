from .base_exporter import BaseExporter


class NgvExporter(BaseExporter):
    def __init__(self):
        pass

    def export(self, graph, routes=None):
        total_nodes = graph.nodes_count()
        total_links = graph.links_count()
        coord_str = self.__get_nodes_positions_string__(graph.nodes())
        links_str = self.__get_links_string(graph.links())
        if routes is not None:
            total_routes = len(routes)
            routes_string = self.__get_routes_string(routes)
        else:
            total_routes = 0
            routes_string = "\n"
        return self.__get_format__() % (total_nodes, total_links, coord_str, links_str, True, total_routes, routes_string)

    @staticmethod
    def __get_format__():
        base_format = "%d\n%d\n%s%s%s\n%d\n%s"
        return base_format

    @staticmethod
    def __get_nodes_positions_string__(nodes):
        result = ""
        for node_label, node in nodes.items():
            aux_str = ";".join(map(str, node.position()))
            result += aux_str + "\n"
        return result

    @staticmethod
    def __get_links_string(links):
        result = ""
        for link in links:
            aux_str = ";".join([link.source().label(), link.destination().label()])
            result += aux_str + "\n"
        return result

    @staticmethod
    def __get_routes_string(routes):
        result = ""
        if routes is None:
            return result
        for route in routes:
            aux_str = ";".join(route)
            result += aux_str + "\n"
        return result

