from setuptools import setup


setup(name='quotes_scraper',
      version='0.2',
      description='Creates quotes from a Goodreads user id.',
      url='https://github.com/jlitven/Quotes-Scraper',
      author='Joshua Litven',
      author_email='jlitven@gmail.com',
      license='MIT',
      packages=['quotes_scraper'],
      entry_points={'console_scripts':
                    ['quotes_scraper = quotes_scraper.quotes_scraper:main']},
      zip_safe=False)
