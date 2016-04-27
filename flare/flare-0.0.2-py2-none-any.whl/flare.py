#!/usr/bin/env python
"""Create a Flare project"""

__version__ = "0.0.2"

import os
import sys
import logging
import subprocess

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
    argument_list = sys.argv

    if len(argument_list) < 3:
        if argument_list[1] in options:
            options[argument_list[1]]()
        else:
            error()
    elif len(argument_list) == 3:
        if argument_list[1] == "new":
            new(argument_list[2])
        else:
            error()
    else:
        error()

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

def error():
    logging.info('Input is not recognized. Try --help to see documentation.')

# def update():
#     subprocess.call(["pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs pip install -U"], shell=True)

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
