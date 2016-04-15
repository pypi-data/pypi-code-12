from setuptools import setup

setup(name='StickShift',
      version='0.1.3',
      description='Database migration tool using raw sql files',
      author='Rohan Panchal',
      author_email='rohan@rohanpanchal.com',
      url='https://www.github.com/rohan-panchal/StickShift',
      install_requires=['psycopg2==2.6.1', 'click==6.2', 'natsort==4.0.4'],
      packages=['stickshift'],
      entry_points={'console_scripts': ["stickshift=stickshift.cli:cli"]},
      test_suite="nose.collector",
      tests_require=["nose"]
      )
