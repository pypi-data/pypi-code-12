#!/usr/bin/env python

import sys
import os
import shutil

TEMPLATE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "template")
MATERIALAPP_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "material_app")

assert os.path.exists(TEMPLATE_PATH), "{} not exist.".format(TEMPLATE_PATH)

if os.path.exists(sys.argv[1]):
    #debug
    NAMEPRETTY = sys.argv[2]
    CURDIR = sys.argv[1]

else:
    NAMEPRETTY = sys.argv[1]
    CURDIR = os.path.abspath(os.curdir)

PACKAGE = "com.yeisoncardona.kickapp"
NAME = NAMEPRETTY.lower().replace("-", "_").replace(" ", "_")
LOCAL = os.path.join(CURDIR, NAMEPRETTY.replace(" ", "_"))
APPDIR = os.path.join(LOCAL, "app")
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

STARTPROJECT = "django-admin startproject {}".format(NAME)
os.system(STARTPROJECT)

SETTINGS_FILE = os.path.join(APPDIR, NAME, NAME, "settings.py")
URLS_FILE = os.path.join(APPDIR, NAME, NAME, "urls.py")

if "--material" in sys.argv:
    #add material template
    shutil.copytree(MATERIALAPP_PATH, os.path.join(APPDIR, NAME, "app"))

    settings = open(SETTINGS_FILE, "r")
    lines = settings.readlines()
    settings.close()
    new_lines = "".join(lines)
    new_lines = new_lines.replace("'django.contrib.staticfiles',", "'django.contrib.staticfiles',\n\n    'app'")
    new_lines += "\nSTATIC_ROOT = os.path.join(BASE_DIR, 'static')\n"

    settings = open(SETTINGS_FILE, "w")
    settings.write(new_lines)
    settings.close()

    urls = open(URLS_FILE, "r")
    lines = urls.readlines()
    urls.close()
    new_lines = "".join(lines)

    new_lines = new_lines.replace("from django.contrib import admin", "from django.contrib import admin\nfrom app.views import Home\nfrom django.conf.urls.static import static\nfrom . import settings")
    new_lines = new_lines.replace("    url(r'^admin/', admin.site.urls),", "    url(r'^$', Home.as_view(), name='home'),\n    url(r'^admin/', admin.site.urls),")
    new_lines = new_lines.replace("]", "] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)")

    urls = open(URLS_FILE, "w")
    urls.write(new_lines)
    urls.close()



EDITFILES = [P4A, MAIN]

PROJECT_ARGS = locals()

#----------------------------------------------------------------------
def main():
    """"""
    try:
        for filename in EDITFILES:
            file = open(filename, "r")
            lines = file.readlines()
            file.close()
            new_lines = "".join(lines)
            new_lines = new_lines.replace("{{", "#&<<").replace("}}", ">>&#")
            new_lines = new_lines.replace("{", "{{").replace("}", "}}")
            new_lines = new_lines.replace("#&<<", "{").replace(">>&#", "}")
            new_lines = new_lines.format(**PROJECT_ARGS)
            file = open(filename, "w")
            file.write(new_lines)
            file.close()
    except Exception as e:
        shutil.rmtree(LOCAL)
        raise e

main()