from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='randomaya',
      version='0.1.10',
      description='Random aya generator',
      long_description = "Generates random aya from the Holy Quran",
      classifiers=[
        'Intended Audience :: Religion',
        'Topic :: Religion',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
      ],
      keywords='Holy Quran Aya Islam Muslim',
      url='https://github.com/ansarb/randomaya',
      author='Ansar Bedharudeen',
      author_email='1ns1rb@gmail.com',
      license='MIT',
      packages=['randomaya'],
      include_package_data=True,
      entry_points = {
        'console_scripts': ['randomaya=randomaya.command_line:main'],
    },
      zip_safe=False)