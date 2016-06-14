"""
Support running the development server.

"""
from argparse import ArgumentParser


def parse_args(graph):
    default_port = graph.config.flask.port

    parser = ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=default_port)
    return parser.parse_args()


def main(graph):
    args = parse_args(graph)
    try:
        graph.flask.run(host=args.host, port=args.port)
    except KeyboardInterrupt:
        pass
