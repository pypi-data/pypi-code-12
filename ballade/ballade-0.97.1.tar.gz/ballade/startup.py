#!/usr/bin/env python3
import tornado
import logging
import signal
import sys
import argparse

from .server import RulesConnector, ProxyServer
from .utils import *
from .config import ConfigManager


def main():

    def signal_handler(signal, frame):
        tornado.ioloop.IOLoop.current().stop()
        server.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(
        description='ballade is a light weight http proxy based on tornado '
                    'and an upstream proxy switcher using SwitchyOmega rules')
    parser.add_argument('-l', '--logging-level', type=str,
                        help='Set debug level in ' + ', '.join(
                            ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'NOTSET']))
    parser.add_argument('-c', '--config-dir', type=str,
                        help='Config directory path like /home/xxx/')
    parser.add_argument('-p', '--process', type=int,
                        help='Number of processes to start with. It is forced to 1 when your platform is windows')
    args = parser.parse_args()
    print("If you need any help, please visit the project repository: https://github.com/holyshawn/ballade")
    print("To check and install update, use \'pip3 install ballade --upgrade\'")

    logging.getLogger().setLevel(getattr(logging, args.logging_level) if args.logging_level else logging.INFO)
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    config_dir = args.config_dir if args.config_dir else None

    config = ConfigManager(config_dir)
    process_number = config.get_process_number(args.process)
    address, port = config.bind

    connector = RulesConnector(config=config)
    server = ProxyServer(connector, config)
    logging.info('Listening on %s:%s', address, port)
    server.bind(port, address)
    server.start(process_number)

    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
