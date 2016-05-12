# -*- coding: utf-8 -*-
import os
from os import path
import sys


MAIN_DIR = os.getcwd()
REQUIREMENTS = "requirements.txt"
CURRENT_REQUIREMENTS = path.join(MAIN_DIR, REQUIREMENTS)


def get_default_after_install_script():
    extra_text = """
def after_install(options, home_dir):
    import os
    import sys
    import subprocess

    def execute(*cmd):
        print("Running: " + " ".join(cmd))
        subprocess.call(cmd)

    if sys.platform == 'win32':
        bin_path = "Scripts"
    else:
        bin_path = "bin"

    pip_path = os.path.join(home_dir, bin_path, 'pip')

    # pip install
"""
    for line in open(CURRENT_REQUIREMENTS, "rb"):
        extra_text += "    execute(pip_path, 'install', '{0}')\n".format(line.strip())
    return extra_text


def create_virtualenv_bootstrap_script(script_path, after_install_script_file):
    import virtualenv

    indented_customize_script = ""
    if after_install_script_file:
        customize_script_lines = open(after_install_script_file, "rb").readlines()
        indented_customize_script = "\n    # customize process\n" + \
                "\n".join(["    " + line.rstrip() for line in customize_script_lines]).rstrip() + \
                "\n"

    script = get_default_after_install_script() + indented_customize_script
    with open(script_path, "wb") as fp:
        fp.write(virtualenv.create_bootstrap_script(script))


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="python -m vebootstrap.{0}".format(path.splitext(path.basename(__file__))[0]))
    parser.add_argument("--output", default="virtualenv-bootstrap.py")
    parser.add_argument("--after-install",  default="")
    args = parser.parse_args()

    create_virtualenv_bootstrap_script(path.join(MAIN_DIR, args.output), args.after_install)

