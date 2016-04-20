from setuptools import setup

setup(name='macrolyzer',
      version='0.1.1',
      description='Macronutrient and weight trend analyzer',
      url='https://github.com/bradgarropy/macrolyzer',
      author='Brad Garropy',
      author_email='bradgarropy@gmail.com',
      license='MIT',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities'],
      packages=['macrolyzer'],
      install_requires=['myfitnesspal'],
      zip_safe=False)
