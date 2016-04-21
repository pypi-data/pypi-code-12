#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import random
import subprocess
import time
import sys


def await(command, cap, base, await_fail, quit_after):
    total_time = 0
    attempt = 0

    while True:
        # Bail out if we've taken too long
        if quit_after != 0 and quit_after <= total_time:
            print 'Took too long, giving up'
            return 1

        failed = False
        print 'Running "{}", attempt: {}'.format(command, attempt)
        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError:
            failed = True

        if (not failed and not await_fail) or (failed and await_fail):
            return 0
        else:  # Backoff
            sleep_time = random.uniform(0, min(cap, base * pow(2, attempt)))
            total_time += sleep_time
            attempt += 1
            time.sleep(sleep_time / 1000.0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='The command to run')
    parser.add_argument('-f', '--await-failure', action='store_true',
                        help='Wait for the command to fail instead of succeed')
    parser.add_argument('-c', '--backoff-cap', default=4000, type=int,
                        help='The maximum amount to wait for in backoff, in milliseconds')
    parser.add_argument('-b', '--backoff-base', default=20, type=int,
                        help='The base amount to backoff by (e.g. the first backoff period) in milliseconds')
    parser.add_argument('-m', '--backoff-max', default=30000, type=int,
                        help='How much time to wait for before giving up, in milliseconds, 0 means try forever')
    args = parser.parse_args()

    return_code = await(args.command, args.backoff_cap, args.backoff_base, args.await_failure, args.backoff_max)
    sys.exit(return_code)


if __name__ == '__main__':
    main()
