from setuptools import setup, find_packages

version = '1.1.4'

requires = [
    'wtforms',
    'Chameleon'
]

test_requires = [
]


setup(name='wtforms_extras',
      version=version,
      description="Provide templates for wtform widgets",
      long_description="""\
""",
      classifiers=[],
      keywords='wtform form widgets',
      author='Nathan Van Gheem',
      author_email='nathan@vangheem.us',
      url='https://github.com/vangheem/wtform_extras',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires + test_requires,
      extras_require={
          'test': test_requires
      },
      test_suite="wtforms_extras",
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
