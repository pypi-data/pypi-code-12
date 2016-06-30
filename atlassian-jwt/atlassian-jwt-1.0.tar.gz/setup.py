from distutils.core import setup

setup(
    name = 'atlassian-jwt',
    packages = ['atlassian_jwt'],
    version = '1.0',
    description = 'JSON web token: pyjwt plus Atlassian query-string-hash claim',
    author = 'Atlassian',
    author_email = 'bedwards@atlassian.com',
    url = 'https://bitbucket.org/atlassian/atlassian-jwt-py',
    keywords = [
        'jwt',
        'json',
        'web',
        'token',
        'pyjwt',
        'atlassian',
        'connect',
        'addon',
        'query',
        'string',
        'hash',        
        'qsh',
    ],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
