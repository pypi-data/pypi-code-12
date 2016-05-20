from setuptools import setup, find_packages

version = '0.1.0'
entry_points = {
    "console_scripts": [
        "sum_rnaseq = sumrnaseq.main.command_line:main1"
    ]
}

setup(name='sumrnaseq.main',
      version=version,
      description='main program',
      long_description="""\
main program""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='main',
      author='Zhi Zhang',
      author_email='zhi.zhang@uni.lu',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['sumrnaseq'],
      include_package_data=True,
      test_suite='nose.collector',
      tests_require=['Nose'],  
      zip_safe=False,
      install_requires=[
          'setuptools',
          'sumrnaseq.makesummary',
          'sumrnaseq.readconfig',
          'sumrnaseq.runrnaseqbash',
          # -*- Extra requirements: -*-
      ],
      entry_points=entry_points,
      )
