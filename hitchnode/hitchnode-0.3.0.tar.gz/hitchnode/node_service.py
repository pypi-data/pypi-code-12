from hitchserve import Service
import sys


class NpmService(Service):
    def __init__(self, node_package, **kwargs):
        self.node_package = node_package
        kwargs['no_libfaketime'] = True
        kwargs['env_vars'] = node_package.environment_vars
        super(NodeService, self).__init__(**kwargs)


class StaticNodeServer(Service):
    def __init__(self, directory, port=8080, **kwargs):
        kwargs['command'] = [
            sys.executable, "-u", "-m", "hitchnode.static_serve",
            "--port", str(port), "--directory", str(directory)
        ]
        kwargs['log_line_ready_checker'] = lambda line: "Static node server running" in line
        super(StaticNodeServer, self).__init__(**kwargs)