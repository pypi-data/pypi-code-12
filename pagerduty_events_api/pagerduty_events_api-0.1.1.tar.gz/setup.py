from setuptools import setup

setup(name='pagerduty_events_api',
      version='0.1.1',
      description='Python wrapper for Pagerduty Events API',
      url='https://github.com/BlasiusVonSzerencsi/pagerduty-events-api',
      download_url='https://github.com/BlasiusVonSzerencsi/pagerduty-events-api/tarball/0.1.1',
      author='Balazs Szerencsi',
      author_email='balazs.szerencsi@icloud.com',
      license='MIT',
      packages=['pagerduty_events_api'],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose', 'ddt'],
      install_requires=['requests'],
      keywords=['pagerduty', 'event', 'api', 'incident', 'trigger', 'acknowledge', 'resolve'])
