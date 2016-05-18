from distutils.core import setup
import os

setup (
	name = "nbacli",
	version = "0.4",
	author = "chenminhua",
	author_email = "chenmh@shanghaitech.edu.cn",
	license = "GPL3",
	description = "watch nba in your cli, of course, no images and videos",
	url = "http://github.com/chenminhua/nba",
	packages = [
		'nba'
	],
	scripts = ['bin/nba'],
	install_requires = [
		'beautifulsoup4 >= 4.4'
	]
)
