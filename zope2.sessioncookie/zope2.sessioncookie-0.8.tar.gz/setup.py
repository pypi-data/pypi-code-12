from setuptools import find_packages
from setuptools import setup


with open('README.rst') as f:
    README = f.read()

with open('CHANGES.rst') as f:
    CHANGES = f.read()

setup(name='zope2.sessioncookie',
      version='0.8',
      description='Allow use of Pyramid-style signed or encrypted cookie '
                  'for scallable Zope2 session storage',
      long_description='\n\n'.join([README, CHANGES]),
      url='https://github.com/zopefoundation/zope2.sessioncookie',
      author='Tres Seaver, Agendaless Consulting',
      author_email='tseaver@agendaless.com',
      license='ZPL 2.1',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: Session",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      packages=find_packages(),
      namespace_packages=['zope2',],
      include_package_data=True,
      install_requires=[
        'pyramid>=1.5',
        'Zope2>=2.13',
      ],
      test_suite='zope2.sessioncookie.tests',
      extras_require={'encrypted': ['pyramid_nacl_session>=0.2']},
)
