from distutils.core import setup

setup(
    name='kitchen_blender',
    version='0.2.1',
    packages=['kitchen_blender'],
    url='https://github.com/monsieurh/rfc_reader',
    license='GPL3',
    author='Martijn Braam',
    author_email='martijn@brixit.nl',
    description='Worker node for the Kitchen Blender render farm',
    keywords="blender farm distributed",
    platforms='any',
    entry_points={
        'console_scripts': [
            'kitchen = kitchen_blender.__init__:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Operating System :: Unix',
    ]
)