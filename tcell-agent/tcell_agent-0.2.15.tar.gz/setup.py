from setuptools import setup, find_packages
from tcell_agent.version import VERSION

setup(name='tcell_agent',
      version=VERSION,
      description='tCell.io Agent',
      url='https://tcell.io',
      author='tCell.io',
      author_email='support@tcell.io',
      license='Free-to-use, proprietary software.',
      install_requires=[
          "requests[security]",
          "future",
          "pyyaml"
      ],
      tests_require=[
          "requests[security]",
          "future",
          "nose",
          "gunicorn",
          "Django",
          "httmock"
      ],
      test_suite = 'nose.collector',
      scripts=['tcell_agent/bin/tcell_agent'],
      packages=find_packages()+['tcell_agent/pythonpath'],
      package_data = { 'tcell_agent.appsensor.rules': ['*.json'] }
)
