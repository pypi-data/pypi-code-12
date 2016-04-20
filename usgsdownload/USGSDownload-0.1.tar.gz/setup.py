from setuptools import setup, find_packages

version = '0.1'

setup(name='USGSDownload',
      version=version,
      description="USGS Download for download landsat data",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Lucas Lamounier',
      author_email='lucasls.oas@gmail.com',
      url='https://github.com/lucaslamounier/USGSDownload/',
      download_url='https://github.com/lucaslamounier/USGSDownload/tarball/0.1',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
)
