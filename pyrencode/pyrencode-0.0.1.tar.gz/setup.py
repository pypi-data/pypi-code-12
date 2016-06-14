from distutils.core import setup


def file_to_list(filename):
    return [line.strip() for line in open(filename).readlines()]

setup(
    name='pyrencode',
    packages=['pyrencode'],
    version='0.0.1',
    description='A pure python rencoder',
    license='MIT',
    long_description=open('README.md',).read(),
    author='Stephanos Papanikolopoulos',
    author_email='spapanik21@gmail.com',
    url='https://github.com/spapanik/pyrencode',
    download_url='https://github.com/spapanik/pyrencode/tarball/0.0.1',
    keywords=file_to_list('KEYWORDS.txt'),
    classifiers=file_to_list('CLASSIFIERS.txt'),
)
