from distutils.core import setup

with open('README.rst') as readme:
    with open('HISTORY.rst') as history:
        long_description = readme.read() + '\n\n' + history.read()

setup(
    install_requires=['requests', 'beautifulsoup4'],
    name='python-vkontakte',
    version='1.1.2',
    packages=['pyvkontakte'],
    url='https://github.com/sashgorokhov/python-vkontakte',
    download_url='https://github.com/sashgorokhov/python-vkontakte/archive/master.zip',
    keywords=['vkontakte', 'api', 'vkontakte api'],
    classifiers=[],
    long_description=long_description,
    license='MIT License',
    author='sashgorokhov',
    author_email='sashgorokhov@gmail.com',
    description='Python library to access vkontakte social network api.'
)