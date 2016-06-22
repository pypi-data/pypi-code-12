from setuptools import setup

setup(
    name='foundation-platform',
    version='0.2.0',

    packages=['tests',
              'foundation_platform', 'foundation_platform.csar',
              'foundation_platform.vnfpi', 'foundation_platform.common',
              'foundation_platform.messaging'],
    url='',
    license='',
    author='Nokia A&A Platform & Parters',
    author_email='cic@nokia.com',
    description='The foundation from which other NFV services are offered.'
)
