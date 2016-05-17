from setuptools import setup

setup(name='um7',
      version='0.3',
      description='Classes to interface with CH Robotics UM7 IMU',
      url='https://pypi.python.org/pypi/um7/0.2',
      author='Daniel Kurek',
      author_email='dkurek93@gmail.com',
      license='MIT',
      packages=['um7'],
      install_requires=['pyserial', 'time', 'binascii', 'struct'],
      zip_safe=False)
