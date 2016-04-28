import os

from setuptools import setup, find_packages

readme = os.path.join(os.path.dirname(__file__), 'README.rst')
with open(readme, 'r') as f:
    readme = f.read()

setup(name='pyramid_prometheus',
      version='0.6',
      description=readme,
      classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "License :: OSI Approved :: MIT License",
        ],
      keywords='pyramid tween statistics metric prometheus',
      author="Brian Sutherland",
      author_email="brian@vanguardistas.net",
      url="https://github.com/jinty/pyramid_prometheus",
      license="MIT",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=['prometheus_client', 'pyramid'],
      )
