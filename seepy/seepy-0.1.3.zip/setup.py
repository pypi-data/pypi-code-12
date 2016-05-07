from distutils.core import setup
setup(
    name='seepy',
    version='0.1.3',
    description='Python script publishing tool',
    long_description = open("README.txt").read(),
    author='Lukasz Laba',
    author_email='lukaszlab@o2.pl',
    url='https://bitbucket.org/lukaszlaba/seepy/wiki/Home',
    packages=['seepy', 'seepy.icons', 'seepy.example_scripts'],
    package_data = {'': ['*.png', '*.md']},
    license = 'GNU General Public License (GPL)',
    keywords = 'notebook ,script, report',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        ],
    )
