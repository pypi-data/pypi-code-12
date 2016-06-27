from distutils.core import setup
setup(
    name='nostril',
    packages=['nostril'],
    version='0.1.1',
    description=('Simple nose wrapper to easily test packages '
                 'from within python.'),
    author='Pedro Paiva',
    author_email='p3k4p4@gmail.com',
    url='https://github.com/pekapa/nostril',
    download_url='https://github.com/pekapa/nostril/tarball/0.1.0',
    keywords=['testing', 'nose'],
    classifiers=[],
    install_requires=['nose'],
)
