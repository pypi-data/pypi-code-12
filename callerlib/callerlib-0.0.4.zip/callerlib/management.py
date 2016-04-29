import os
import shutil
import argparse


def startproject():
    parser = argparse.ArgumentParser()
    parser.add_argument('proj_dir_name', help='callerlib project directory name')
    args = parser.parse_args()

    base_dir = os.getcwd()
    proj_dir_name = args.proj_dir_name
    abs_dir = os.path.join(base_dir, proj_dir_name)
    template_dir = os.path.join(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)), 'template')

    shutil.copytree(template_dir, abs_dir)
