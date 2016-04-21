from .ngv_exporter import NgvExporter


class GraphExporter:
    def __init__(self, driver=None):
        if driver == "ngv":
            self.__exporter = NgvExporter()
        else:
            raise Exception("Driver: %s not found\n" % driver)

    def export(self, graph, routes=None):
        return self.__exporter.export(graph, routes)
