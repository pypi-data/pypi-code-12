#!/usr/bin/env python

import sys
import os
import shutil

TEMPLATE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "template")
assert os.path.exists(TEMPLATE_PATH), "{} not exist.".format(TEMPLATE_PATH)

NAMEPRETTY = sys.argv[1]
PACKAGE = "www.yeisoncardona.kickapp"
NAME = NAMEPRETTY.lower().replace("-", "_").replace(" ", "_")

LOCAL = os.path.join(os.path.abspath(os.curdir), NAMEPRETTY.replace(" ", "_"))
APPDIR = os.path.join(LOCAL, "app")
STARTPROJECT = "django-admin startproject {}".format(NAME)
P4A = os.path.join(LOCAL, ".p4a")
MAIN = os.path.join(LOCAL, "app", "main.py")

ICON = os.path.join(APPDIR, "resources", "icon.png")

ANDROID_SDK = "/opt/android-sdk"
ANDROID_SDK_API = "21"

CRYSTAX_NDK_VERSION = "10.3.1"
CRYSTAX_NDK =  os.path.expanduser("~/crystax-ndk-{}".format(CRYSTAX_NDK_VERSION))

PORT = "8000"

shutil.copytree(TEMPLATE_PATH, LOCAL)
os.chdir(APPDIR)
os.system(STARTPROJECT)

EDITFILES = [P4A, MAIN]

PROJECT_ARGS = locals()

#----------------------------------------------------------------------
def main():
    """"""
    try:
        for filename in EDITFILES:
            file = open(filename, "r")
            lines = file.readlines()
            new_lines = "".join(lines)
            new_lines = new_lines.replace("{{", "#&<<").replace("}}", ">>&#")
            new_lines = new_lines.replace("{", "{{").replace("}", "}}")
            new_lines = new_lines.replace("#&<<", "{").replace(">>&#", "}")
            new_lines = new_lines.format(**PROJECT_ARGS)
            file.close()
            file = open(filename, "w")
            file.write(new_lines)
            file.close()
    except Exception as e:
        shutil.rmtree(LOCAL)
        raise e

#if __name__ == "__main__":
main()