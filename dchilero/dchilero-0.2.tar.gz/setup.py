from setuptools import setup

setup(name='dchilero',
      version='0.2',
      description='command line for chilero micro framework',
      url='https://keller_matta@bitbucket.org/keller_matta/dchilero.git',
      author='Keller Obdulio Matta Calderón',
      author_email='kellermaca@gmail.com',
      entry_points={
          'console_scripts': [
              'chilero = dchilero.cli:main',
          ],
      },
      license='MIT',
      packages=['dchilero'],
      zip_safe=False)