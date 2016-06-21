from setuptools import setup

import org_e

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='org_e',
      version='0.1',
      description='Organizes files into folders based on type, declutters your life',
	  classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
		'Operating System :: OS Independent'
      ],
	  keywords='organize declutter clutter organizing',
      url='https://gitlab.com/rsnk96/Org_E',
      author='R S Nikhil Krishna',
      author_email='rsnk96@gmail.com',
      license='MIT',
      packages=['org_e'],
	  install_requires=[
          'tqdm',
          'termcolor',
      ],
      include_package_data=True,
      zip_safe=False,
	  entry_points={
	        'console_scripts': [
	            'org_e = org_e.__init__:main',
	        ],
	    },
)