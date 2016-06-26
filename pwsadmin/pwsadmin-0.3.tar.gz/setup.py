from distutils.core import setup

def parse_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()

setup(
    name = 'pwsadmin',
    version = '0.3',
    packages = ['pwsadmin'],
    author = 'Kyle Stevenson',
    author_email = 'kyle@kylestevenson.me',
    description = 'A simple wrapper around the Pro Wager Systems backoffice software.',
    download_url = 'https://github.com/kylestev/pwsadmin/tarball/0.3',
    keywords = 'pro wager systems',
    license = 'MIT',
    url = 'https://github.com/kylestev/pwsadmin'
)
