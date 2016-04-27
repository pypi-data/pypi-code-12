import subprocess
import os


def create(path):
    subprocess.call(["virtualenv {}/venv".format(path)], shell=True)

def remove():
    subprocess.call(["rm -rf venv"], shell=True)

def start():
    subprocess.call(["source venv/bin/activate"], shell=True)

def stop():
    subprocess.call(["deactivate"], shell=True)
