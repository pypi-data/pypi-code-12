#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# setup.py --- Setup script for flo-check-homework
# Copyright (c) 2013, 2014, 2016  Florent Rougon
#
# This file is part of flo-check-homework.
#
# flo-check-homework is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# flo-check-homework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston,
# MA  02110-1301 USA.

import sys
import os
import subprocess
import traceback
from distutils.core import setup

import flo_check_homework       # To access flo_check_homework.version_info

PYPKG_NAME = "flo-check-homework"  # PyPI package name
PYPKG = "flo_check_homework"    # name of the main Python package
MAIN_PROGNAME = "flo-check-homework" # name of the main program
DECORATE_PROGNAME = os.path.join("tools", "flo-check-homework-decorate-games",
                                 "flo-check-homework-decorate-games")

from flo_check_homework import __version__ as VERSION
VERSION_NOSUFFIX = '.'.join([ str(i)
                              for i in flo_check_homework.version_info[:3] ])

# This function must be run from the root directory of the Git repository.
def writeChangelogData(output=None, firstCommit=None, ChangeLog_start=None):
    args = ["gitlog-to-changelog", "--format=%s%n%n%b%n"]
    if firstCommit is not None:
        args.extend(["--", "{0}..".format(firstCommit)])

    try:
        subprocess.check_call(args, stdout=output)
    except os.error:
        print(traceback.format_exc(), file=sys.stderr)

        print("""\
Error (see above for a traceback): unable to run {prg}
================================================={underlining}
Maybe this program is not installed on your system. You can download it from:

  {url}

Note: if you have problems with the infamous shell+Perl crap in the first lines
of that file, you can replace it with a simple shebang line such as
"#! /usr/bin/perl".""".format(
   prg=args[0],
   underlining="=" * len(args[0]),
   url="http://git.savannah.gnu.org/gitweb/?p=gnulib.git;a=blob_plain;"
       "f=build-aux/gitlog-to-changelog"), file=sys.stderr)
        sys.exit(1)

    if ChangeLog_start is not None:
        with open(ChangeLog_start, "r", encoding="utf-8") as orig_ch:
            output.write("\n" + orig_ch.read())


# This function must be run from the root directory of the Git repository.
def generateChangelog(ch_name, write_to_stdout=False):
    firstCommit = "b854546837c229e17e8e2e4e7cf44f429129e496"
    ChangeLog_start = "ChangeLog.init"

    print("Converting the Git log into ChangeLog format...", end=' ',
          file=sys.stderr)

    if write_to_stdout:
        writeChangelogData(output=None, firstCommit=firstCommit,
                           ChangeLog_start=ChangeLog_start)
    else:
        tmp_ch_name = "{0}.new".format(ch_name)

        try:
            with open(tmp_ch_name, "w", encoding="utf-8") as tmp_ch:
                writeChangelogData(output=tmp_ch, firstCommit=firstCommit,
                                   ChangeLog_start=ChangeLog_start)

            os.rename(tmp_ch_name, ch_name)
        finally:
            if os.path.exists(tmp_ch_name):
                os.unlink(tmp_ch_name)

    print("done.", file=sys.stderr)


def do_setup():
    # Using the Qt resource system for images wastes a lot of space and is
    # quite ugly: we need the images in the source package (for the user to
    # see or modify); with PyQt resources, they would also be translated into
    # a huge string inside a hideous .py file full of \xYY escapes which
    # takes 4 times the size of the original images (!); and if this wasn't
    # enough, the .py file would be byte-compiled into a .pyc file that has
    # approximately the same size as the original images.
    # Therefore, we are loading the images by means of pkgutil.get_data()
    # instead. This unfortunately implies that they will be stored in the same
    # directory (or zip file or egg...) as PYPKG. This is not the best
    # location according to the FHS, but will be fixed when distutils2 becomes
    # usable (if ever).
    #
    # create_resource_file("fch_resources.qrc",
    #                      os.path.join(PYPKG, "fch_resources.py"))
    with open("README.rst", "r", encoding="utf-8") as f:
        long_description = f.read()

    setup(name=PYPKG_NAME,
          version=VERSION,
          description="A program that allows to run other programs only after "
          "a set of questions have been correctly answered",
          long_description=long_description,
          author="Florent Rougon",
          author_email="f.rougon@free.fr",
          url="http://frougon.net/",
          download_url=\
              "http://frougon.net/projects/flo-check-homework/"
          "dist/{}/{}-{}.tar.bz2".format(VERSION_NOSUFFIX, PYPKG_NAME,
                                         VERSION),
          keywords=[PYPKG_NAME, "education", "learning", "calculus", "grammar"],
          requires=["PyQt4 (>=4.9)"],
          classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 5 - Production/Stable",
            "Environment :: X11 Applications :: Qt",
            "Environment :: Win32 (MS Windows)",
            "Environment :: MacOS X",
            "Intended Audience :: Education",
            "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
            "Operating System :: OS Independent",
            "Topic :: Education :: Computer Aided Instruction (CAI)"],
          packages=[PYPKG, "{0}.conjugations".format(PYPKG)],
          package_data={PYPKG: ["translations/*/*.qm",
                                "images/*.png",
                                "images/logo/*.png",
                                "images/rewards/10-abysmal/*.jpg",
                                "images/rewards/20-not_good_enough/*.jpg",
                                "images/rewards/20-not_good_enough/*.png",
                                "images/rewards/30-happy/*.jpg",
                                "images/rewards/30-happy/*.png",
                                "images/rewards/40-very_happy/*.jpg",
                                "images/rewards/40-very_happy/*.png"]},
          scripts=[MAIN_PROGNAME, DECORATE_PROGNAME])


def main():
    ch_name = "ChangeLog"
    if os.path.isdir(".git"):
        generateChangelog(ch_name)
    elif not os.path.isfile(ch_name):
        msg = """\
There is no {cl!r} file here and it seems you are not operating from a
clone of the Git repository (no .git directory); therefore, it is impossible to
generate the {cl!r} file from the Git log. Aborting.""".format(cl=ch_name)
        sys.exit(msg)

    do_setup()

if __name__ == "__main__": main()
