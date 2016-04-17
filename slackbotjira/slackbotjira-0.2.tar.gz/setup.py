from setuptools import setup

setup(name='slackbotjira',
      version='0.2',
      description='Slackbot JIRA Plugin',
      url='tbd',
      author='Kyle Varga',
      author_email='slackbot-jira@kylevarga.com',
      install_requires=[line.strip() for line in open('requirements.txt')],
      license='MIT',
      packages=['slackbotjira'],
      zip_safe=False)