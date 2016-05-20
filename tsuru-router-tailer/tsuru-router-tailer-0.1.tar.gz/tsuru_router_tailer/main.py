import tsuru_router_tailer.runner as runner

import argparse


def main():
    parser = argparse.ArgumentParser(description='''
    Tail tsuru route and send to logstash''')
    parser.add_argument('log', help='path to log file')
    parser.add_argument('--logstash', required=True, help='logstash URL')
    args = parser.parse_args()

    runner.Runner(
        log_path=args.log,
        logstash=args.logstash
    ).run()
