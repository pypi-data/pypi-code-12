import setuptools

try:
   import pypandoc
   readme = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, OSError, RuntimeError):
   readme = ''

setuptools.setup(
    name="hug_peewee_connect",
    version="0.0.2",
    url="https://github.com/soloman1124/hug_peewee_connect",

    author="Soloman Weng",
    author_email="soloman1124@gmail.com",

    description="Simple and clean integration with the peewee ORM",
    long_description=readme,

    packages=setuptools.find_packages(),

    install_requires=['hug', 'peewee'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
