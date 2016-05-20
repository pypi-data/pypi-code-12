import argparse
import logging

import tsuru_router_tailer.runner as runner


def main():
    parser = argparse.ArgumentParser(description='''
    Tail tsuru route and send to logstash''')
    parser.add_argument('log', help='path to log file')
    parser.add_argument('--logstash', required=True, help='logstash URL')
    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='debug'
    )
    args = parser.parse_args()

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    log = logging.getLogger('tsuru-router-tailer')

    log.debug(
        "Watching: {} Sending to: {}".format(
            args.log,
            args.logstash
        )
    )
    runner.Runner(
        log_path=args.log,
        logstash=args.logstash
    ).run()
