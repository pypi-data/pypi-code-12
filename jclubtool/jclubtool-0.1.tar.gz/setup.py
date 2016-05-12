from setuptools import setup

setup(name='jclubtool',
      version='0.1',
      description='Python 3 PDF Reader and Image Snippet Collection Tool',
      url='http://github.com/neuroneuro15/jclubtool',
      author='Nicholas A Del Grosso',
      author_email='delgrosso.nick@gmail.com',
      license='MIT',
      packages=['jclubtool'],
      scripts=['jclublauncher'],
      install_requires=[
            'Wand',
            'Pillow',
            'appdirs',
      ],
      zip_safe=False)
