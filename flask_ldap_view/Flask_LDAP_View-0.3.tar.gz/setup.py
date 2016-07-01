



from distutils.core import setup
setup(
  name = 'Flask_LDAP_View',
  packages = ['Flask_LDAP_View'], 
  version = '0.3',
  license='MIT',
  description = 'A library to restrict your flask pages by LDAP groups',
  author = 'John McGrath',
  author_email = 'john.mcgrath207@gmail.com',
  url = 'https://github.com/sonance207/Flask_LDAP_View',
  download_url = 'https://github.com/sonance207/Flask_LDAP_View/tarball/0.3', 
  keywords = ['Flask', 'LDAP', 'Security'], 
   install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

