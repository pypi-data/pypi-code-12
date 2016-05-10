from setuptools import setup, find_packages

setup(name='django-softdeletev2',
      version='0.4.2',
      description='Soft delete support for Django ORM, with undelete.',
      author='Sachin Prabhu',
      author_email='sachin.prabhu@kuliza.com',
      maintainer='Steve Coursen',
      maintainer_email='sachin.prabhu@kuliza.com',
      url="https://github.com/galacticsurfer/django-softdelete",
      packages=find_packages(),
      install_requires=['setuptools',],
      include_package_data=True,
      setup_requires=['setuptools_hg',],
      classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        ]
)
