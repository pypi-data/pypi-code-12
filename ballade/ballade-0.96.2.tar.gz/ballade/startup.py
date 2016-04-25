#!/usr/bin/env python3
import tornado
import logging
import signal
import sys
import argparse
import yaml

from .server import RulesConnector, ProxyServer
from .utils import *


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
    config_dir = args.config_dir if args.config_dir else get_config_dir()
    if not config_dir:
        print("Please define a config directory by -c, there is no $HOME($HOMEPATH) in your environment variables")
        exit(1)
    if not os.path.exists(config_dir):
        print("Cannot find exist config directory, use %s" % config_dir)
        init_config_dir(config_dir)
    num_processes = args.process if args.process else 0

    config = yaml.load(open(os.path.join(config_dir, 'config.yaml'), 'r'))
    regex_path = os.path.join(config_dir, 'regex')
    omega_path = os.path.join(config_dir, config['omega_file'])
    omega_converter(config, omega_path, regex_path)

    connector = RulesConnector(path=regex_path, config=config)
    server = ProxyServer(connector)
    address, port = config['bind']['address'], config['bind']['port']
    logging.info('Listening on %s:%s', address, port)
    server.bind(port, address)
    if sys.platform == 'win32':
        # Windows does not support os.fork() which is indispensable for tornado
        num_processes = 1  # Only one process
    server.start(num_processes)  # Auto number process for logical cores

    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
