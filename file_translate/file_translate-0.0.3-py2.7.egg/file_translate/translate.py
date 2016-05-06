# -*- coding: utf-8 -*-
# (C) Copyright Digital Catapult Limited 2016
import argparse
import json
import os
import re


def convert(config_file, input_file, output_file):
    # Read in the config file
    with open(config_file, 'r') as content_file:
        config = json.load(content_file)

    # Read in the content
    with open(input_file, 'r') as content_file:
        content = content_file.read()

    # Convert the content
    for translation in config['translations']:
        search = translation['search'].encode()
        replace = translation['replace'].encode()
        content = re.sub(search, replace, content)

    # Write out the content
    with open(output_file, 'w') as content_file:
        content_file.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-c',
            '--config',
            help='Configuration file',
            default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json'))
    parser.add_argument(
            '-i',
            '--input',
            help='Input file',
            required=True)
    parser.add_argument(
            '-o',
            '--output',
            help='Output file',
            required=True)
    args = parser.parse_args()
    convert(args.config, args.input, args.output)

if __name__ == '__main__':
    main()