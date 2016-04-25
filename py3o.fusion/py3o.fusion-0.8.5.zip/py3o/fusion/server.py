from py3o.fusion.log import logging
import argparse

from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource
from twisted.internet import reactor

import pkg_resources

from py3o.fusion.formpage import FormPage
from py3o.fusion.indexpage import RootPage
from py3o.fusion.featurespage import FeaturesPage


def cmd_line_server():
    logging.info("py3o.fusion server starting")
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Activate debug traceback on the client side",
    )

    argparser.add_argument(
        "-p", "--listenport",
        dest="listen_port",
        help="specify the PORT on which our service will listen",
        metavar="PORT",
        default=8765)

    argparser.add_argument(
        "-s", "--renderserver",
        dest="render_server",
        help="specify the hostname/ip of the render server",
        metavar="RENDERSERVER",
        default=None)

    argparser.add_argument(
        "-r", "--renderport",
        dest="render_port",
        help="specify the PORT on which the renderserver is available",
        metavar="RPORT",
        default=8994)

    args = argparser.parse_args()

    logging.info("listing on port: %s" % args.listen_port)
    start_server(args)


def start_server(options):

    reactor.suggestThreadPoolSize(30)

    root = Resource()
    root.putChild(
        "static",
        File(
            pkg_resources.resource_filename("py3o.fusion", "static")
        )
    )
    root.putChild("", RootPage())

    formpage = FormPage(
        options.render_server,
        int(options.render_port),
        clientdebug=options.debug
    )

    root.putChild("form", formpage)
    root.putChild("features", FeaturesPage())
    factory = Site(root)
    reactor.listenTCP(int(options.listen_port), factory)
    reactor.run(installSignalHandlers=1)
