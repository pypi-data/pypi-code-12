import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages
setup(
    name = "McImage",
    version = "0.2",
    packages = find_packages(),
    scripts = ['mcimage.py'],

    
    install_requires = ['beautifulsoup4 >= 4', 'requests >= 2'],

   
    # metadata for upload to PyPI
    author = "Darryl McClellan",
    author_email = "darryljm34@gmail.com",
    description = "Bulk image downloader command line tool",
    license = "GNU GPL",
    keywords = "image download downloader picture pictures .jpg bulk automatic picture",


    # could also include long_description, download_url, classifiers, etc.
)
