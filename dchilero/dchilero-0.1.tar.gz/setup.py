import setuptools

setup_params= dict(
      name='dchilero',
      version='0.1',
      package='dchilero',
      description='command line for chilero micro framework',
      include_package_data=True,
      url='https://keller_matta@bitbucket.org/keller_matta/dchilero.git',
      author='Keller Obdulio Matta Calderón',
      author_email='kellermaca@gmail.com',
      entry_points={
          'console_scripts': [
              'chilero = dchilero.cli:main',
          ],
      },
      license='MIT',
      setup_requires=[
        'setuptools_scm',
      ],
    )

if __name__ == '__main__':
    setuptools.setup(**setup_params)