from setuptools import setup, find_packages

setup(name='dappr',
      packages=find_packages(),
      version='0.4.4',
      description='Django app for registration, with an approval step.',
      url='https://github.com/millanp/dappr',
      author='Millan Philipose',
      author_email='millanmakes@gmail.com',
      license='MIT',
      install_requires=[
          'Django>=1.8',
      ],
      package_data={'dappr': ['templates/registration/*.html', 'templates/registration/*.txt']},
      install_package_data=True
)
