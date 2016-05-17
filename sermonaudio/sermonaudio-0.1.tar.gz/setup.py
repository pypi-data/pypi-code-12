from setuptools import setup

try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst', outputfile='README.rst')
except ImportError:
    print('WARNING: Package being build without ReST documentation. Please install pypandoc.')
    readme = None

setup(name='sermonaudio',
      version='0.1',
      description='The official Python client library for accessing the SermonAudio.com APIs',
      long_description=readme,
      classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
      ],
      url='http://api.sermonaudio.com/',
      author='SermonAudio.com',
      author_email='info@sermonaudio.com',
      keywords='sermon audio API preaching church bible',
      license='MIT',
      packages=['sermonaudio', 'sermonaudio.node'],
      install_requires=[
            'requests>=2.9',
            'pytz>=2016.3'
      ])
