#!/usr/bin/env python
"""Create a Flare project"""

__version__ = "0.0.6"

import os
import sys
import logging
import subprocess
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    options = {
    # "start": start,
    # "stop": stop,
    # "remove": remove,
    # "update": update,
    "--help": docs
    }

    parser = argparse.ArgumentParser(description="Flare Project Builder")
    # group = parser.add_mutually_exclusive_group()
    parser.add_argument("new", help="Create new Flare project")
    parser.add_argument("name", help="Create new Flare project")
    args = parser.parse_args()
    if args.new:
        new(args.name)
    elif args.update:
        update()


def new(path):
    root_path = "{}/{}".format(os.getcwd(), path)
    if not os.path.exists(root_path):
        logging.info('Creating %s', root_path)
        top_level_files = ["LICENSE", "README.md", "requirements.txt"]
        top_level_directories = ["data", "docs", "models", "notebooks", "ref", "reports", "src"]
        data_directories = ["raw", "temp", "prod"]
        src_directories = ["features", "models"]
        os.mkdir(root_path)
        create(root_path)
        for f in top_level_files:
            open("{}/{}".format(root_path, f), 'a').close()
        for directory in top_level_directories:
            os.mkdir(os.path.join(root_path, directory))
        for directory in data_directories:
            os.mkdir(os.path.join("{}/data/".format(root_path), directory))
        for directory in src_directories:
            os.mkdir(os.path.join("{}/src/".format(root_path), directory))
    else:
        logging.info('Directory %s already exists', path)

def update():
    subprocess.call(["pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U"], shell=True)

def docs():
    print("""
    Run "flare new <project-name> to create a new Flare project with a venv"
    Run "flare start to start the venv"
    Run "flare stop to stop the venv"
    Run "flare update to update the Pip packages within the venv"
    Run "flare remove to remove the venv"
    """)

def create(path):
    subprocess.call(["virtualenv {}/venv".format(path)], shell=True)

# def remove():
#     subprocess.call(["rm -rf {}/venv".format(os.getcwd())], shell=True)
#
# def start():
#     os.system("source {}/venv/bin/activate".format(os.getcwd()))
#     # subprocess.call(["source {}/venv/bin/activate".format(os.getcwd())], shell=True)
#
# def stop():
#     os.system("{} deactivate".format(os.getcwd()))
#     # subprocess.call(["{} deactivate".format(os.getcwd())], shell=True)

if __name__ == '__main__':
    main()
