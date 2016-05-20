from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='Products.Doormat',
      version=version,
      description="Adds a doormat viewlet and installs it in the Plone "
                  "footer. The links and text in the doormat are manageable "
                  "as content. ",
      long_description=(open("README.txt").read() + "\n" +
                        open("CHANGES.rst").read() +
                        open(os.path.join("docs", "DEVELOPERS.txt")).read() +
                        open(os.path.join("docs", "TODO.txt")).read()),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.3",
          "Intended Audience :: End Users/Desktop",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet",
          "Topic :: Scientific/Engineering :: GIS",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='doormat viewlet plone footer',
      author='Kees Hink',
      author_email='hink@gw20e.com',
      url='https://github.com/collective/Products.Doormat',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'unittest2',
          ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      # If you really need to add local stuff and want to use paster
      # for it, you can uncomment these lines and run 'python
      # setup.py' again:
      #setup_requires=["PasteScript"],
      #paster_plugins=["ZopeSkel"],
      )
