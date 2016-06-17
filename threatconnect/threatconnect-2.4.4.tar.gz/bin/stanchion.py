#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A command line tool for testing App Engine apps.

It feeds the app command line arguments. This simulates the way that
Apps are started in the TC Exchange runtime environment.
"""

import argparse
import ConfigParser
import os
import subprocess


def main():
    """Main function for the tool."""
    parser = argparse.ArgumentParser()

    parser.add_argument('target', metavar='TARGET', help='Target python script to test')

    args, unknown = parser.parse_known_args()

    working_dir = os.getcwd()

    config = ConfigParser.RawConfigParser()
    config_file = os.path.join(working_dir, 'app.conf')
    config.read(config_file)

    log_path = working_dir
    arguments = ['--tc_log_path', log_path]

    for argument, datum in config.defaults().items():
        arguments.extend([argument, datum])

    command = ['python', args.target]
    command.extend(arguments)

    subprocess.call(command)
