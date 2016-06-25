from setuptools import setup, find_packages


setup(name='jps_plot',
      version='0.0.2',
      description='json plot using jps',
      author='Takashi Ogura',
      author_email='t.ogura@gmail.com',
      url='http://github.com/OTL/jps_plot',
      packages=find_packages(exclude=['test', 'docs']),
      install_requires=[
          'jps',
          'matplotlib>=1.5.1',
        ],
      entry_points= {
        'console_scripts': [
            'jps_plot = jps_plot.jps_plot:main',
            ]
        }
      )
