from distutils.core import setup
setup(
    name = 'notes-py',
    packages = ['notes_py'],
    version = '0.0.1',
    description = 'A dumb static site generator.',
    author = 'Maximilian Friedersdorff',
    author_email = 'max@friedersdorff.com',
    license='GPL',
    url = 'https://github.com/maxf130/notes-py',
    download_url = 'https://github.com/maxf130/notes-py/tarball/0.0.1',
    keywords = ['site generator'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires = ['CommonMark>=0.6,<0.7'],
    entry_points={
        'console_scripts': [
            'compile_notes=notes_py.notes:main',
        ],
    },
)
