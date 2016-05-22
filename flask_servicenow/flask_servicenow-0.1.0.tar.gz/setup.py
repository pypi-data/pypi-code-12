try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='flask_servicenow',
    packages=['flask_servicenow'],
    version='0.1.0',
    description='ServiceNow REST API Flask extension',
    install_requires=['servicenow_rest'],
    author='Robert Wikman',
    author_email='rbw@vault13.org',
    maintainer='Robert Wikman',
    maintainer_email='rbw@vault13.org',
    url='https://github.com/rbw0/flask-servicenow',
    download_url='https://github.com/rbw0/flask-servicenow/tarball/0.1.0',
    keywords=['servicenow', 'rest', 'api', 'flask'],
    classifiers=[],
    license='GPLv2',
)
