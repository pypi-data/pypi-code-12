from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='shopify-scraper',
      version='0.1',
      description='Shopify Reviews Scraper',
      url='https://github.com/danielfv/shopify_review_scraper',
      author='Daniel Valverde',
      author_email='danielfvalverde@gmail.com',
      license='MIT',
      packages=['shopify_scraper'],
      install_requires=[
      	"mechanize",
      	"lxml",
      ],
      keywords = ['shopify', 'scraper', 'review'], # arbitrary keywords
      zip_safe=False)
