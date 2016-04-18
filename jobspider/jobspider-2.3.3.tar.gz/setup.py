"""
jobspider
-----

jobspider can crawl several websites,we can get any data using some keyword

Jobspider is Useful
````````````

Save in a hello.py:

.. code:: python

    from jobpiser import Spider


    if __name__ == "__main__":
         spider = Spider('python')
         spider.single_run('lagou')

And Easy to Setup
`````````````````

And run it:

.. code:: bash

    $ pip install jobspider
    $ python hello.py


Links
`````
* `development version
  <https://github.com/haipersist/jobspider>`_

"""

from setuptools import setup



setup(
    name='jobspider',
    version='2.3.3',
    url='https://github.com/haipersist/jobspider',
    license='BSD',
    author='Haibo Wang',
    author_email='393993705@qq.com',
    description='A spider that crawls the job infos of famous website ',
    long_description=__doc__,
    packages=['jobspider','jobspider.baseclass','jobspider.baseclass.utils'],
    package_data={'jobspider': ['*.cfg']},
    package_dir={'jobspider': 'jobspider'},
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'requests>=2.8.1',
        'beautifulsoup4>=4.4.1',
        'xlutils>=1.7.1',
        'xlrd>=0.9.4',
        'xlwt>=1.0.0',
        'html5lib',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    #entry_points='''
     #   [console_scripts]
      #  jobspider=jobspider.spider:main
    #'''
)
