#!/usr/bin/env python2

from distutils.core import setup
import sys
import glob
import os
from os.path import expanduser
home = expanduser("~")

if 'bdist_wheel' in sys.argv:
    raise RuntimeError("This setup.py does not support wheels")

if (sys.version_info[0]*10 + sys.version_info[1]) < 26:
    raise RuntimeError('Sorry, Python < 2.6 is not supported')

setup(
	name             = "football_score_indicator",
	version          = "4.5.9.5",
	author           = "Nishant Kukreja, Abhishek",
	author_email     = "kukreja34@gmail.com",
        maintainer       = "Nishant Kukreja",
        maintainer_email = "rawcoder@openmailbox.org",
	description      = "An indicator to show live football scores in panel",
	license          = "GPLv3",
	keywords         = "Cricket Scores Live Indicator Applet AppIndicator Unity GTK",
	url              = "https://github.com/rawcoder/football-score-applet",
	packages         = ["football_score_indicator"],
	data_files       = [(sys.prefix + "/share/pixmaps", glob.glob("icons/*")),
	                    (sys.prefix + "/share/applications", ["footballscores_indicator.desktop"])],
	scripts          = ["footballscores_indicator"],
	long_description = open("README").read(),
        requires         = ["requests", "gi.repository"],
        classifiers      = [
            'Development Status :: 5 - Production/Stable',
            'Programming Language :: Python',
            'Environment :: X11 Applications :: Gnome',
            'Environment :: X11 Applications :: GTK',
            'Environment :: Web Environment',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
            'Operating System :: POSIX :: Linux',
            'Topic :: Desktop Environment :: Gnome',
            'Topic :: Internet'
          ]
        )
#os.chmod(home +"/settings.cfg",0o777)
print sys.prefix
