import setuptools

import versioneer

#DESCRIPTION_FILES = ["pypi-intro.rst"]
#
#long_description = []
#import codecs
#for filename in DESCRIPTION_FILES:
#    with codecs.open(filename, 'r', 'utf-8') as f:
#        long_description.append(f.read())
#long_description = "\n".join(long_description)


setuptools.setup(
    name = "stringtopy",
    version = versioneer.get_version(),
    packages = setuptools.find_packages(),
    install_requires = [],
    author = "James Tocknell",
    author_email = "aragilar@gmail.com",
    description = "",
    #long_description = long_description,
    license = "3-clause BSD",
    keywords = "strings",
    url = "http://stringtopy.rtfd.io",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    cmdclass=versioneer.get_cmdclass(),
)
