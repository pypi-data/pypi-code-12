from distutils.core import setup
from codecs import open

setup(
    name = 'uoftscrapers',
    packages = [
        'uoftscrapers',
        'uoftscrapers.scrapers.utils',
        'uoftscrapers.scrapers.courses',
        'uoftscrapers.scrapers.buildings',
        'uoftscrapers.scrapers.textbooks',
        'uoftscrapers.scrapers.food',
        'uoftscrapers.scrapers.calendar',
        'uoftscrapers.scrapers.timetable',
        'uoftscrapers.scrapers.exams',
        'uoftscrapers.scrapers.athletics',
        'uoftscrapers.scrapers.parking',
        'uoftscrapers.scrapers.shuttle'
    ],
    version = '0.4.3',
    description = 'University of Toronto public web scraping scripts.',
    author = 'Qasim Iqbal',
    author_email = 'me@qas.im',
    url = 'https://github.com/cobalt-io/uoft-scrapers',
    download_url = 'https://github.com/cobalt-uoft/uoft-scrapers/tarball/0.4.3',
    package_data = {'': ['LICENSE.md']},
    package_dir = {'uoftscrapers': 'uoftscrapers'},
    include_package_data = True,
    keywords = ['uoft', 'scraper', 'toronto', 'university of toronto', 'cobalt'],
    install_requires = ['requests>=2.6.2', 'beautifulsoup4>=4.3.2', 'pytidylib>=0.2.4', 'lxml>=3.6.0', 'pytz>=2016.3'],
    classifiers = []
)
