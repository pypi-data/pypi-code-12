from setuptools import setup, find_packages
import sys, os

version = '0.2.1'

setup(name='family',
      version=version,
      description="Easy to create your microservice based on multiple python frameworks.",
      long_description="""\
""",
      keywords='microservice falcon flask',
      author='torpedoallen',
      author_email='torpedoallen@gmail.com',
      url='https://github.com/daixm/family',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'click',
          'PasteScript',
          'check-manifest',
      ],
      entry_points="""
      [console_scripts]
      family-createapp=family.commands.createapp:create
      [paste.paster_create_template]
      falcon = family.templates.basic:FalconTemplate
      flask = family.templates.basic:FlaskTemplate
      """,
      )
