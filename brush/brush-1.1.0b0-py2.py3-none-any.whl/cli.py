"""Command-line interface for brush."""

import os.path as osp

from tornado.options import options
from tornado.ioloop import IOLoop

from .comb import FrequencyComb, DummyFrequencyComb


def read_config_file(path):
    """Open a configuration file and return it as a dict."""
    path = osp.abspath(osp.expanduser(path))
    if not osp.exists(path):
        return
    else:
        options.parse_config_file(path, final=False)


def main(testing=False):
    """Command-line interface entry point."""
    options.parse_command_line()
    from .sweep import Sweep

    if options.offline or testing:
        comb = DummyFrequencyComb()
        options.debug = True
    else:
        comb = FrequencyComb(options.xmlrpc_host, options.xmlrpc_port,
                             options.xmlrpc_user, options.xmlrpc_password)

    sweep = Sweep(comb)
    if not testing:
        IOLoop.instance().run_sync(lambda: sweep.run())

if __name__ == "__main__":
    main()
