from setuptools import setup, find_packages

import os
import platform

if 'IT4I_FACTORY_PREBUILD' in os.environ and os.environ['IT4I_FACTORY_PREBUILD']:
    setup_kwargs = {'setup_requires': ['mustache',
                                       'pystache',
                                       'setuptools-git-version',
                                       'setuptools-markdown'],
                    'version_format': '{tag}',
                    'long_description_markdown_filename': 'README.md'}
else:
    from version import version
    setup_kwargs = {'setup_requires': [],
                    'version': version}

platform_fullinfo = platform.platform()
df_prefix = '' if 'ubuntu'.lower() in platform_fullinfo.lower() else 'local/'

setup(name='it4i.portal.clients',
      description='Client tools for accessing various client APIs of IT4I portals',
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='accounting api client extranet feed it4i it4innovations it4i.portal.clients it4i-portal-clients motd pbs portal rss tool',
      author='IT4Innovations',
      author_email='support@it4i.cz',
      url='http://www.it4i.cz/',
      license='IT4I',
      packages=find_packages(),
      data_files=[('%setc/it4i-portal-clients/' % (df_prefix), ['it4i/portal/clients/templates/motd_rss.pt-sample',
                                                                'it4i/portal/clients/conf/main.cfg-sample'])],
      namespace_packages=['it4i', 'it4i.portal'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'ConfigParser',
          'beautifulsoup4',
          'chameleon',
          'feedparser',
          'lxml',
          'simplejson',
          'tabulate',
      ],
      entry_points={
          'console_scripts': ['it4ifree = it4i.portal.clients.it4ifree:main',
                              'motd_rss = it4i.portal.clients.motd_rss:main']
      },
      **setup_kwargs)
