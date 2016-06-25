import argparse
import logging
import asyncio
import signal

from apslite_agent import constants
from apslite_agent.config import get_config
from apslite_agent.consumer import OdinCloudConsumer


def parse_command_line():
    parser = argparse.ArgumentParser(constants.PACKAGE_NAME)

    parser.add_argument('--config', '-c', default='config.yml',
                        help="Configuration file to use")
    parser.add_argument('--loglevel', '-l', default='ERROR',
                        choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                        help="Set logging level")

    return parser.parse_args()


def main():
    args = parse_command_line()
    config = get_config(filename=args.config)

    oa_id = config['oa']['id']
    loglevel = config.get('logging', {}).get('level', 'ERROR')

    logging.basicConfig(level=min(getattr(logging, args.loglevel),
                                  getattr(logging, loglevel, logging.ERROR)),
                        format=constants.LOG_FORMAT)

    consumer = OdinCloudConsumer(config, oa_id, args.config)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, loop.stop)
    loop.run_until_complete(consumer())
    loop.run_forever()


if __name__ == '__main__':
    main()
