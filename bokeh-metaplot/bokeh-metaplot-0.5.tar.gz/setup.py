from distutils.core import setup
setup(
    name = 'bokeh-metaplot',
    packages = ['bokeh_metaplot'], # this must be the same as the name above
    version = '0.5',
    description = 'a enhanced bokeh plot type which can including some additional infomation inside',
    author = 'Wu Young',
    author_email = 'doomsplayer@gmail.com',
    url = 'https://github.com/doomsplayer/bokeh-metaplot', # use the URL to the github repo
    download_url = 'https://github.com/doomsplayer/bokeh-metaplot/tarball/0.1', # I'll explain this in a second
    keywords = ['bokeh', 'plot', 'metadata'], # arbitrary keywords
    install_requires = ['bokeh', 'multipledispatch'],
    classifiers = [],
)
