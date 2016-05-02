from distutils.core import setup
setup(
    name='seepy',
    version='0.0.2',
    description='Python script visualisation tool',
    long_description = open("README.txt").read(),
    author='Lukasz Laba',
    author_email='lukaszlab@o2.pl',
    url='https://www.struthon.org',
    packages=['seepy', 'seepy.icons', 'seepy.example_scripts'],
    package_data = {'': ['*.png']},
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
