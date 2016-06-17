from distutils.core import setup

setup(
	name = 'GangGang',
	version = '0.3',
	description = 'A library to use a remote server to execute code, mainly for GhPython in Grasshopper3D.',
	author = 'Dan Taeyoung',
	author_email = 'provolot@gmail.com',
	url = 'https://github.com/provolot/GangGang', # use the URL to the github repo
	download_url = 'https://github.com/provolot/GangGang/tarball/0.3', 
    license="GPLv3",
    py_modules=['GangGang'],
    entry_points = """
      [console_scripts]
      GangGang = GangGang:GangGang
    """

)
