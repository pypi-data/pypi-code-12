from setuptools import setup
setup(
    name='lsoc',
    packages=['lsoc'],
    version='0.1.2',
    description='Lite Python package that lets you view file and directory access rights with octal',
    author='Alper Sakarya',
    author_email='alpersakarya@gmail.com',
    url='https://github.com/AlperSakarya/lsoc',
    download_url='https://github.com/AlperSakarya/lsoc/tarball/0.1',
    keywords=['ls', 'octal'],
    classifiers=[],
    entry_points={'console_scripts': ['lsoc = lsoc.lsoc:lsoccmd']}
)
